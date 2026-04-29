function batch_repeat444_and_export_inp()
% After batch_generate_curved_x finishes, run this script to:
% 1) read every .mat in batch_curved_x/mat/
% 2) repeat voxel to 4x4x4
% 3) save repeated .mat into batch_curved_x/4x4x4_mat/
% 4) export each repeated .mat into Abaqus .inp in Output/
%
% Current project standard:
% - specimen repetition = [4 4 4]
% - nVoxel per cell = 80
% - voxelSize = [0.25 0.25 0.25] mm

clear; clc;

%% ===================== PATH SETTINGS =====================
rootDir   = 'D:\Simulation\Curved_Rod_Voxel_Model';   % 根目录需要修改
srcMatDir = fullfile(rootDir, 'batch_curved_x', 'mat');
repMatDir = fullfile(rootDir, 'batch_curved_x', '4x4x4_mat');
outInpDir = fullfile(rootDir, 'Output');

if ~exist(srcMatDir, 'dir')
    error('Source MAT folder not found: %s', srcMatDir);
end
if ~exist(repMatDir, 'dir'); mkdir(repMatDir); end
if ~exist(outInpDir, 'dir'); mkdir(outInpDir); end

%% ===================== PARALLEL SETTINGS =================
desiredWorkers = 4;   %启用并行池
p = gcp('nocreate');
if isempty(p)
    parpool('local', desiredWorkers);
elseif p.NumWorkers ~= desiredWorkers
    delete(p);
    parpool('local', desiredWorkers);
end

%% ===================== PROJECT SETTINGS ==================
repeatN = [4 4 4];% 4x4x4点阵矩阵
opts = struct();
opts.voxelSize = [0.25 0.25 0.25];
opts.nodeSetTop = 'N_TOP_FIX';
opts.nodeSetBottom = 'N_BOTTOM_FIX';

overwriteExisting = true;   % true = 覆盖已有 rep444.mat / .inp

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

    repFile = fullfile(repMatDir, [baseName '_rep444.mat']);
    inpFile = fullfile(outInpDir, [baseName '_rep444.inp']);

    % skip if already done
    if ~overwriteExisting && exist(repFile, 'file') && exist(inpFile, 'file')
        continue;
    end

    S = load(srcFile);
    if ~isfield(S, 'voxel')
        warning('Skip %s: missing variable "voxel".', files(i).name);
        continue;
    end

    voxel = repmat(logical(S.voxel), repeatN);

    save_repeat444_mat(repFile, voxel, repeatN, S);

    export_mat_voxel_to_abaqus_inp(repFile, inpFile, opts);
end

fprintf('\nAll done.\n');
fprintf('Repeated MAT folder: %s\n', repMatDir);
fprintf('INP output folder  : %s\n', outInpDir);
end