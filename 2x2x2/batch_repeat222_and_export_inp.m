function batch_repeat222_and_export_inp()
% After batch_generate_curved_x finishes, run this script to:
% 1) read every .mat in batch_curved_x/mat/
% 2) repeat voxel to 2x2x2
% 3) save repeated .mat into batch_curved_x/2x2x2_mat/
% 4) export each repeated .mat into Abaqus .inp in Output/
%
% Current project standard:
% - specimen repetition = [2 2 2]
% - nVoxel per cell = 80
% - voxelSize = [0.25 0.25 0.25] mm

clear; clc;

%% ===================== PATH SETTINGS =====================
rootDir = fileparts(mfilename('fullpath'));  % current 2x2x2 folder
if isempty(rootDir); rootDir = pwd; end
srcMatDir = fullfile(rootDir, 'batch_curved_x', 'mat');
repMatDir = fullfile(rootDir, 'batch_curved_x', '2x2x2_mat');
outInpDir = fullfile(rootDir, 'Output');

if ~exist(srcMatDir, 'dir')
    error('Source MAT folder not found: %s', srcMatDir);
end
if ~exist(repMatDir, 'dir'); mkdir(repMatDir); end
if ~exist(outInpDir, 'dir'); mkdir(outInpDir); end

%% ===================== PARALLEL SETTINGS =================
desiredWorkers = 4;   % parallel pool for export
p = gcp('nocreate');
if isempty(p)
    parpool('local', desiredWorkers);
elseif p.NumWorkers ~= desiredWorkers
    delete(p);
    parpool('local', desiredWorkers);
end

%% ===================== PROJECT SETTINGS ==================
repeatN = [2 2 2];
opts = struct();
opts.voxelSize = [0.25 0.25 0.25];
opts.nodeSetTop = 'N_TOP_FIX';
opts.nodeSetBottom = 'N_BOTTOM_FIX';

overwriteExisting = true;   % true = overwrite existing rep222.mat / .inp

%% ===================== FIND MAT FILES ====================
files = dir(fullfile(srcMatDir, '*.mat'));
if isempty(files)
    error('No .mat files found in: %s', srcMatDir);
end

fprintf('Found %d MAT files in %s\n', numel(files), srcMatDir);
fprintf('Workers = %d\n', gcp().NumWorkers);
drawnow;

%% ===================== MAIN PARFOR =======================
parfor i = 1:numel(files)
    srcFile = fullfile(files(i).folder, files(i).name);
    [~, baseName, ~] = fileparts(files(i).name);

    repFile = fullfile(repMatDir, [baseName '_rep222.mat']);
    inpFile = fullfile(outInpDir, [baseName '_rep222.inp']);

    if ~overwriteExisting && exist(repFile, 'file') && exist(inpFile, 'file')
        continue;
    end

    S = load(srcFile);
    if ~isfield(S, 'voxel')
        warning('Skip %s: missing variable "voxel".', files(i).name);
        continue;
    end

    voxel = repmat(logical(S.voxel), repeatN);

    save_repeat222_mat(repFile, voxel, repeatN, S);

    export_mat_voxel_to_abaqus_inp(repFile, inpFile, opts);
end

fprintf('\nAll done.\n');
fprintf('Repeated MAT folder: %s\n', repMatDir);
fprintf('INP output folder  : %s\n', outInpDir);
end
