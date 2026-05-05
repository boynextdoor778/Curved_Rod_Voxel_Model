function batch_export_mat_voxel_to_stl_222()
clear; clc;

%% ===================== PATH SETTINGS =====================
rootDir = fileparts(mfilename('fullpath'));  % current 2x2x2 folder
if isempty(rootDir); rootDir = pwd; end

srcMatDir = fullfile(rootDir, 'batch_curved_x', '2x2x2_mat');
outStlDir = fullfile(rootDir, 'STL');

if ~exist(srcMatDir, 'dir')
    error('Source MAT folder not found: %s', srcMatDir);
end
if ~exist(outStlDir, 'dir'); mkdir(outStlDir); end

%% ===================== PARALLEL SETTINGS =================
desiredWorkers = 8;

p = gcp('nocreate');
if isempty(p)
    parpool('local', desiredWorkers);
elseif p.NumWorkers ~= desiredWorkers
    delete(p);
    parpool('local', desiredWorkers);
end

%% ===================== STL SETTINGS ======================
% 100% physical size: 2x2x2 specimen is about 40 mm high.
voxelSize = [0.25 0.25 0.25];

overwriteExisting = true;   % true = overwrite existing STL

%% ===================== FIND MAT FILES ====================
files = dir(fullfile(srcMatDir, '*.mat'));
if isempty(files)
    error('No .mat files found in: %s', srcMatDir);
end

fprintf('Found %d MAT files in %s\n', numel(files), srcMatDir);
fprintf('Workers = %d\n', gcp().NumWorkers);
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

%% ===================== MAIN PARFOR =======================
parfor i = 1:numel(files)
    matFile = matFiles{i};
    stlFile = stlFiles{i};

    try
        if ~overwriteExisting && exist(stlFile, 'file')
            status{i} = 'Skipped';
        else
            export_one_mat_to_stl(matFile, stlFile, voxelSize);
            status{i} = 'Done';
        end
    catch ME
        status{i} = ['Failed: ' ME.message];
    end
end

%% ===================== SUMMARY ===========================
T = table(matFiles, stlFiles, status, ...
    'VariableNames', {'MAT_File', 'STL_File', 'Status'});

summaryFile = fullfile(outStlDir, 'stl_export_summary.csv');
writetable(T, summaryFile);

fprintf('\nAll done.\n');
fprintf('STL folder: %s\n', outStlDir);
fprintf('Summary: %s\n', summaryFile);

end
