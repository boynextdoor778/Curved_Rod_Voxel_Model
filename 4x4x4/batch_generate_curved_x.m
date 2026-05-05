function batch_generate_curved_x
clear; clc;

%% ===================== PATH SETTINGS =====================
rootDir = fileparts(mfilename('fullpath'));  % current 2x2x2 or 4x4x4 folder
if isempty(rootDir); rootDir = pwd; end
outRoot = fullfile(rootDir, 'batch_curved_x');

if ~exist(rootDir, 'dir'); mkdir(rootDir); end
if ~exist(outRoot, 'dir'); mkdir(outRoot); end

topoOutDir = fullfile(outRoot, 'topology');
matOutDir  = fullfile(outRoot, 'mat');
figOutDir  = fullfile(outRoot, 'preview');

if ~exist(topoOutDir, 'dir'); mkdir(topoOutDir); end
if ~exist(matOutDir, 'dir'); mkdir(matOutDir); end
if ~exist(figOutDir, 'dir'); mkdir(figOutDir); end

%% ================= PARALLEL SETTINGS =====================
desiredWorkers = 8;   % MATLAB parallel pool; start with 8 if hardware allows

p = gcp('nocreate');
if isempty(p)
    parpool('local', desiredWorkers);
elseif p.NumWorkers ~= desiredWorkers
    delete(p);
    parpool('local', desiredWorkers);
end

%% ================= FIXED GEOMETRY SETTINGS ================
nPtsPerArm = 61;
refAxis    = [0 0 1];
nVoxel     = 80; % 60-100. Higher = better geometry but slower/larger.

%% ================= RANDOM SAMPLING SETTINGS ===============
targetN = 16; % target number of accepted samples
rngSeed = 1;
rng(rngSeed);

radiusMin = 0.032; % strut radius minimum
radiusMax = 0.041; % strut radius maximum
bendMin   = 0.06;  % bend amplitude minimum
bendMax   = 0.12;  % bend amplitude maximum

useDensityFilter = true;
densityMin = 0.022;
densityMax = 0.046;

trialFactor = 1.5;
Ntrial = ceil(targetN * trialFactor);

savePreviewPNG = true; % set false if preview generation is slow
previewEvery = 4;

fprintf('RUN SETTINGS | rootDir=%s | targetN=%d | Ntrial=%d | nVoxel=%d | workers=%d\n', ...
    rootDir, targetN, Ntrial, nVoxel, gcp().NumWorkers);
drawnow;

%% ================ PRE-GENERATE RANDOM SAMPLES ============
radiusSamples  = radiusMin + (radiusMax - radiusMin) * rand(Ntrial,1);
bendAmpSamples = bendMin   + (bendMax   - bendMin)   * rand(Ntrial,1);

%% ==================== RESULT CONTAINERS ===================
Accepted = false(Ntrial,1);
Density  = nan(Ntrial,1);
Radius   = radiusSamples;
BendAmp  = bendAmpSamples;
CaseName = strings(Ntrial,1);
TopoFile = strings(Ntrial,1);
MatFile  = strings(Ntrial,1);
PngFile  = strings(Ntrial,1);

%% ======================= MAIN PARFOR ======================
parfor i = 1:Ntrial
    radius  = radiusSamples(i);
    bendAmp = bendAmpSamples(i);

    caseName = sprintf('cx_rand_%05d_b%03d_r%03d', ...
        i, round(1000*bendAmp), round(1000*radius));

    topoFile = fullfile(topoOutDir, [caseName '.txt']);
    matFile  = fullfile(matOutDir, [caseName '.mat']);
    pngFile  = fullfile(figOutDir, [caseName '.png']);

    acceptedLocal = false;
    density = nan;

    write_curved_x_topology(topoFile, nPtsPerArm, bendAmp, refAxis);
    [voxel, density] = GenerateVoxel(nVoxel, topoFile, radius);

    if ~useDensityFilter || (density >= densityMin && density <= densityMax)
        acceptedLocal = true;

        save_sample_mat(matFile, voxel, density, radius, bendAmp, ...
            nPtsPerArm, refAxis, nVoxel, topoFile);

        if savePreviewPNG && mod(i, previewEvery) == 0
            voxelRep = repmat(voxel, [3 3 3]);

            fig = figure('Visible','off', 'Color','k');
            pch = patch(isosurface(double(voxelRep), 0.5));
            isonormals(double(voxelRep), pch);
            set(pch, 'FaceColor', [0.2 0.9 0.4], 'EdgeColor', 'none');

            daspect([1 1 1]);
            axis tight; axis off;
            view(35,22);
            camlight headlight;
            lighting gouraud;
            title(sprintf('%s | density = %.4f', caseName, density), 'Color','w');

            exportgraphics(fig, pngFile, 'Resolution', 180);
            close(fig);
        else
            pngFile = "";
        end
    else
        if exist(topoFile, 'file')
            delete(topoFile);
        end
        topoFile = "";
        matFile = "";
        pngFile = "";
    end

    Accepted(i) = acceptedLocal;
    Density(i)  = density;
    CaseName(i) = string(caseName);
    TopoFile(i) = string(topoFile);
    MatFile(i)  = string(matFile);
    PngFile(i)  = string(pngFile);
end

%% =================== FILTER FINAL SAMPLES =================
acceptedIdx = find(Accepted);

if numel(acceptedIdx) < targetN
    warning('Only %d accepted samples were found. Increase trialFactor or relax the density filter.', ...
        numel(acceptedIdx));
    keepIdx = acceptedIdx;
else
    keepIdx = acceptedIdx(1:targetN);
end

extraIdx = setdiff(acceptedIdx, keepIdx);

for ii = 1:numel(extraIdx)
    idx = extraIdx(ii);

    if strlength(TopoFile(idx)) > 0 && exist(TopoFile(idx), 'file')
        delete(TopoFile(idx));
    end
    if strlength(MatFile(idx)) > 0 && exist(MatFile(idx), 'file')
        delete(MatFile(idx));
    end
    if strlength(PngFile(idx)) > 0 && exist(PngFile(idx), 'file')
        delete(PngFile(idx));
    end
end

T = table( ...
    (1:numel(keepIdx)).', ...
    CaseName(keepIdx), ...
    Radius(keepIdx), ...
    BendAmp(keepIdx), ...
    Density(keepIdx), ...
    TopoFile(keepIdx), ...
    MatFile(keepIdx), ...
    PngFile(keepIdx), ...
    'VariableNames', {'CaseID','CaseName','Radius','BendAmp','Density','TopoFile','MatFile','PngFile'});

summaryFile = fullfile(outRoot, 'summary_random.csv');
writetable(T, summaryFile);

fprintf('Finished. Accepted kept: %d\n', height(T));
fprintf('Summary: %s\n', summaryFile);
end
