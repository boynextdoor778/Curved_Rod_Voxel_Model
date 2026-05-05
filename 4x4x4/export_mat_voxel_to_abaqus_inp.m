function export_mat_voxel_to_abaqus_inp(matFile, inpFile, opts)
% EXPORT_MAT_VOXEL_TO_ABAQUS_INP
% Convert one saved MAT voxel model into a compact Abaqus INP.
%
% This compact version writes only nodes used by active voxel elements.
% It avoids exporting the full structured background grid, so 4x4x4 INP
% files are much smaller than the full-grid version.

if nargin < 3 || isempty(opts)
    opts = struct();
end

if ~isfield(opts, 'voxelSize');      opts.voxelSize = [1 1 1]; end
if ~isfield(opts, 'partName');       opts.partName = 'LATTICE'; end
if ~isfield(opts, 'elementType');    opts.elementType = 'C3D8'; end
if ~isfield(opts, 'elementSetName'); opts.elementSetName = 'EALL'; end
if ~isfield(opts, 'nodeSetTop');     opts.nodeSetTop = 'N_TOP'; end
if ~isfield(opts, 'nodeSetBottom');  opts.nodeSetBottom = 'N_BOTTOM'; end

S = load(matFile);
if ~isfield(S, 'voxel')
    error('MAT file does not contain variable "voxel": %s', matFile);
end

voxel = logical(S.voxel);
[nx, ny, nz] = size(voxel);
dx = opts.voxelSize(1);
dy = opts.voxelSize(2);
dz = opts.voxelSize(3);

activeIdx = find(voxel);
numElem = numel(activeIdx);
if numElem == 0
    error('Voxel model contains no active elements: %s', matFile);
end

fprintf('Compact INP export | active elements = %d | grid = %d x %d x %d\n', ...
    numElem, nx, ny, nz);

% nodeMap maps structured corner index (i,j,k) to compact Abaqus node ID.
nodeMap = zeros(nx+1, ny+1, nz+1, 'uint32');
maxNodeEstimate = uint32(numElem * 8);
nodeIJK = zeros(double(maxNodeEstimate), 3, 'uint32');
elemConn = zeros(numElem, 8, 'uint32');

% Surface node buffers. Overallocated; trimmed later.
bottomNodes = zeros(numElem * 4, 1, 'uint32');
topNodes    = zeros(numElem * 4, 1, 'uint32');
botCount = 0;
topCount = 0;
nodeCount = uint32(0);

[ii, jj, kk] = ind2sub([nx, ny, nz], activeIdx);

for e = 1:numElem
    i = ii(e);
    j = jj(e);
    k = kk(e);

    corners = uint32([ ...
        i,   j,   k; ...
        i+1, j,   k; ...
        i+1, j+1, k; ...
        i,   j+1, k; ...
        i,   j,   k+1; ...
        i+1, j,   k+1; ...
        i+1, j+1, k+1; ...
        i,   j+1, k+1]);

    conn = zeros(1, 8, 'uint32');

    for c = 1:8
        ci = corners(c,1);
        cj = corners(c,2);
        ck = corners(c,3);

        nid = nodeMap(ci, cj, ck);
        if nid == 0
            nodeCount = nodeCount + 1;
            nid = nodeCount;
            nodeMap(ci, cj, ck) = nid;
            nodeIJK(double(nid), :) = [ci, cj, ck];
        end
        conn(c) = nid;
    end

    elemConn(e, :) = conn;

    if k == 1
        bottomNodes(botCount+1:botCount+4) = conn(1:4);
        botCount = botCount + 4;
    end

    if k == nz
        topNodes(topCount+1:topCount+4) = conn(5:8);
        topCount = topCount + 4;
    end
end

nodeIJK = nodeIJK(1:double(nodeCount), :);
bottomNodes = unique(bottomNodes(1:botCount), 'stable');
topNodes    = unique(topNodes(1:topCount), 'stable');

if isempty(bottomNodes)
    error('No bottom surface nodes were detected.');
end
if isempty(topNodes)
    error('No top surface nodes were detected.');
end

fid = fopen(inpFile, 'w');
if fid == -1
    error('Cannot open output INP file: %s', inpFile);
end
cleaner = onCleanup(@() fclose(fid)); %#ok<NASGU>

fprintf(fid, '*Heading\n');
fprintf(fid, '** Compact INP generated from MAT voxel file: %s\n', matFile);
fprintf(fid, '** Active elements: %d, active nodes: %d\n', numElem, nodeCount);
fprintf(fid, '*Preprint, echo=NO, model=NO, history=NO, contact=NO\n');
fprintf(fid, '*Part, name=%s\n', opts.partName);

% ---------------- Nodes ----------------
fprintf(fid, '*Node\n');
for nid = 1:double(nodeCount)
    i = double(nodeIJK(nid,1));
    j = double(nodeIJK(nid,2));
    k = double(nodeIJK(nid,3));
    x = (i - 1) * dx;
    y = (j - 1) * dy;
    z = (k - 1) * dz;
    fprintf(fid, '%d, %.8f, %.8f, %.8f\n', nid, x, y, z);
end

% ---------------- Elements ----------------
fprintf(fid, '*Element, type=%s, elset=%s\n', opts.elementType, opts.elementSetName);
for eid = 1:numElem
    c = elemConn(eid, :);
    fprintf(fid, '%d, %d, %d, %d, %d, %d, %d, %d, %d\n', ...
        eid, c(1), c(2), c(3), c(4), c(5), c(6), c(7), c(8));
end

% ---------------- Boundary node sets ----------------
write_id_list(fid, opts.nodeSetBottom, bottomNodes);
write_id_list(fid, opts.nodeSetTop, topNodes);

fprintf(fid, '*End Part\n');
fprintf(fid, '*Assembly, name=ASSEMBLY\n');
fprintf(fid, '*Instance, name=%s-1, part=%s\n', opts.partName, opts.partName);
fprintf(fid, '*End Instance\n');
fprintf(fid, '*End Assembly\n');

fprintf('INP exported: %s\n', inpFile);
fprintf('Active nodes exported: %d\n', nodeCount);
end

function write_id_list(fid, setName, ids)
fprintf(fid, '*Nset, nset=%s\n', setName);
for i = 1:numel(ids)
    if i < numel(ids)
        fprintf(fid, '%d, ', ids(i));
    else
        fprintf(fid, '%d\n', ids(i));
    end
    if mod(i, 16) == 0
        fprintf(fid, '\n');
    end
end
if isempty(ids) || mod(numel(ids), 16) ~= 0
    % final newline already handled by the last fprintf above
end
end
