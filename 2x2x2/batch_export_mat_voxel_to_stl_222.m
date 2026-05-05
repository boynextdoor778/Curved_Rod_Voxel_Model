function batch_export_mat_voxel_to_stl_222()
clear; clc;

%% ===================== PATH SETTINGS =====================
rootDir = fileparts(mfilename('fullpath'));  % current 2x2x2 folder
if isempty(rootDir); rootDir = pwd; end
addpath(rootDir);

srcMatDir = fullfile(rootDir, 'batch_curved_x', '2x2x2_mat');
outStlDir = fullfile(rootDir, 'STL');

if ~exist(srcMatDir, 'dir')
    error('Source MAT folder not found: %s', srcMatDir);
end
if ~exist(outStlDir, 'dir'); mkdir(outStlDir); end

%% ===================== STL SETTINGS ======================
% 100% physical size: 2x2x2 specimen is about 40 mm high.
voxelSize = [0.25 0.25 0.25];
overwriteExisting = true;   % true = overwrite existing STL

% Use false first for debugging. After confirmed, set true for batch speed.
useParallel = false;
desiredWorkers = 8;

%% ===================== FIND MAT FILES ====================
files = dir(fullfile(srcMatDir, '*.mat'));
if isempty(files)
    error('No .mat files found in: %s', srcMatDir);
end

fprintf('Found %d MAT files in %s\n', numel(files), srcMatDir);
fprintf('STL output folder: %s\n', outStlDir);
drawnow;

matFiles = cell(numel(files), 1);
stlFiles = cell(numel(files), 1);
status   = cell(numel(files), 1);

for i = 1:numel(files)
    matFiles{i} = fullfile(files(i).folder, files(i).name);
    [~, baseName, ~] = fileparts(files(i).name);
    stlFiles{i} = fullfile(outStlDir, [baseName '.stl']);
    status{i} = 'Pending';
end

%% ===================== MAIN EXPORT =======================
if useParallel
    p = gcp('nocreate');
    if isempty(p)
        parpool('local', desiredWorkers);
    elseif p.NumWorkers ~= desiredWorkers
        delete(p);
        parpool('local', desiredWorkers);
    end

    parfor i = 1:numel(files)
        status{i} = export_one_case(matFiles{i}, stlFiles{i}, voxelSize, overwriteExisting);
    end
else
    for i = 1:numel(files)
        fprintf('[%d/%d] %s\n', i, numel(files), matFiles{i});
        status{i} = export_one_case(matFiles{i}, stlFiles{i}, voxelSize, overwriteExisting);
        fprintf('    %s\n', status{i});
    end
end

%% ===================== SUMMARY ===========================
T = table(matFiles, stlFiles, status, ...
    'VariableNames', {'MAT_File', 'STL_File', 'Status'});

summaryFile = fullfile(outStlDir, 'stl_export_summary.csv');
writetable(T, summaryFile);

nDone = sum(strcmp(status, 'Done'));
nSkipped = sum(strcmp(status, 'Skipped'));
nFailed = numel(status) - nDone - nSkipped;

fprintf('\nAll done.\n');
fprintf('Done    : %d\n', nDone);
fprintf('Skipped : %d\n', nSkipped);
fprintf('Failed  : %d\n', nFailed);
fprintf('STL folder: %s\n', outStlDir);
fprintf('Summary: %s\n', summaryFile);

if nFailed > 0
    fprintf('\nFailed cases:\n');
    for i = 1:numel(status)
        if startsWith(status{i}, 'Failed')
            fprintf('%s | %s\n', matFiles{i}, status{i});
        end
    end
end

end

function status = export_one_case(matFile, stlFile, voxelSize, overwriteExisting)
try
    if ~overwriteExisting && exist(stlFile, 'file')
        status = 'Skipped';
        return;
    end

    export_one_mat_to_stl(matFile, stlFile, voxelSize);

    if exist(stlFile, 'file')
        status = 'Done';
    else
        status = 'Failed: export finished but STL file was not created';
    end
catch ME
    status = ['Failed: ' ME.message];
end
end
