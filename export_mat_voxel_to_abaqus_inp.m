function export_mat_voxel_to_abaqus_inp(matFile, inpFile, opts)
% EXPORT_MAT_VOXEL_TO_ABAQUS_INP
% Convert one saved sample MAT (containing 'voxel') into a basic Abaqus INP.
%
% INPUTS
%   matFile : e.g. 'D:\Simulation\4.26\mat\.mat'
%   inpFile : output Abaqus .inp path
%   opts    : struct with optional fields
%       .voxelSize      = [dx dy dz] physical size of one voxel, default [1 1 1]
%       .partName       = 'LATTICE'
%       .elementType    = 'C3D8'
%       .elementSetName = 'EALL'
%       .nodeSetTop     = 'N_TOP'
%       .nodeSetBottom  = 'N_BOTTOM'
%       .zTol           = 1e-9
%
% NOTE
% This exports ONLY the deformable voxel specimen mesh.
% Material / contact / platen / BC / step definitions should be added later
% in Abaqus Python or by appending more INP sections.

if nargin < 3 || isempty(opts)
    opts = struct();
end

if ~isfield(opts, 'voxelSize');      opts.voxelSize = [1 1 1]; end
if ~isfield(opts, 'partName');       opts.partName = 'LATTICE'; end
if ~isfield(opts, 'elementType');    opts.elementType = 'C3D8'; end
if ~isfield(opts, 'elementSetName'); opts.elementSetName = 'EALL'; end
if ~isfield(opts, 'nodeSetTop');     opts.nodeSetTop = 'N_TOP'; end
if ~isfield(opts, 'nodeSetBottom');  opts.nodeSetBottom = 'N_BOTTOM'; end
if ~isfield(opts, 'zTol');           opts.zTol = 1e-9; end

S = load(matFile);
if ~isfield(S, 'voxel')
    error('MAT file does not contain variable "voxel": %s', matFile);
end

voxel = logical(S.voxel);
[nx, ny, nz] = size(voxel);
dx = opts.voxelSize(1);
dy = opts.voxelSize(2);
dz = opts.voxelSize(3);

% Node ID mapping for structured grid corners
nodeId = @(i,j,k) i + (nx+1)*(j-1) + (nx+1)*(ny+1)*(k-1);

fid = fopen(inpFile, 'w');
if fid == -1
    error('Cannot open output INP file: %s', inpFile);
end
cleaner = onCleanup(@() fclose(fid)); %#ok<NASGU>

fprintf(fid, '*Heading\n');
fprintf(fid, '** Generated from MAT voxel file: %s\n', matFile);
fprintf(fid, '*Preprint, echo=NO, model=NO, history=NO, contact=NO\n');
fprintf(fid, '*Part, name=%s\n', opts.partName);

% ---------------- Nodes ----------------
fprintf(fid, '*Node\n');
nid = 1;
for k = 1:(nz+1)
    z = (k-1) * dz;
    for j = 1:(ny+1)
        y = (j-1) * dy;
        for i = 1:(nx+1)
            x = (i-1) * dx;
            fprintf(fid, '%d, %.8f, %.8f, %.8f\n', nid, x, y, z);
            nid = nid + 1;
        end
    end
end

% ---------------- Elements ----------------
fprintf(fid, '*Element, type=%s, elset=%s\n', opts.elementType, opts.elementSetName);
eid = 1;
for k = 1:nz
    for j = 1:ny
        for i = 1:nx
            if voxel(i,j,k)
                n1 = nodeId(i,   j,   k);
                n2 = nodeId(i+1, j,   k);
                n3 = nodeId(i+1, j+1, k);
                n4 = nodeId(i,   j+1, k);
                n5 = nodeId(i,   j,   k+1);
                n6 = nodeId(i+1, j,   k+1);
                n7 = nodeId(i+1, j+1, k+1);
                n8 = nodeId(i,   j+1, k+1);
                fprintf(fid, '%d, %d, %d, %d, %d, %d, %d, %d, %d\n', ...
                    eid, n1, n2, n3, n4, n5, n6, n7, n8);
                eid = eid + 1;
            end
        end
    end
end

% ---------------- Boundary node sets (global top/bottom only) ----------------
topNodeMask = false((nx+1), (ny+1), (nz+1));
bottomNodeMask = false((nx+1), (ny+1), (nz+1));

% ---- bottom surface: only global bottom layer k = 1 ----
k = 1;
for j = 1:ny
    for i = 1:nx
        if ~voxel(i,j,k)
            continue;
        end

        % bottom face nodes of element (i,j,1)
        bottomNodeMask(i,   j,   k) = true;
        bottomNodeMask(i+1, j,   k) = true;
        bottomNodeMask(i+1, j+1, k) = true;
        bottomNodeMask(i,   j+1, k) = true;
    end
end

% ---- top surface: only global top layer k = nz ----
k = nz;
for j = 1:ny
    for i = 1:nx
        if ~voxel(i,j,k)
            continue;
        end

        % top face nodes of element (i,j,nz)
        topNodeMask(i,   j,   k+1) = true;
        topNodeMask(i+1, j,   k+1) = true;
        topNodeMask(i+1, j+1, k+1) = true;
        topNodeMask(i,   j+1, k+1) = true;
    end
end

bottomNodes = [];
topNodes = [];

for k = 1:(nz+1)
    for j = 1:(ny+1)
        for i = 1:(nx+1)
            nid_here = nodeId(i,j,k);

            if bottomNodeMask(i,j,k)
                bottomNodes(end+1) = nid_here; %#ok<AGROW>
            end

            if topNodeMask(i,j,k)
                topNodes(end+1) = nid_here; %#ok<AGROW>
            end
        end
    end
end

bottomNodes = unique(bottomNodes, 'stable');
topNodes    = unique(topNodes, 'stable');

if isempty(bottomNodes)
    error('No bottom surface nodes were detected.');
end
if isempty(topNodes)
    error('No top surface nodes were detected.');
end

write_id_list(fid, opts.nodeSetBottom, bottomNodes);
write_id_list(fid, opts.nodeSetTop, topNodes);

fprintf(fid, '*End Part\n');
fprintf(fid, '*Assembly, name=ASSEMBLY\n');
fprintf(fid, '*Instance, name=%s-1, part=%s\n', opts.partName, opts.partName);
fprintf(fid, '*End Instance\n');
fprintf(fid, '*End Assembly\n');

fprintf('INP exported: %s\n', inpFile);
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
if ~isempty(ids) && mod(numel(ids),16) ~= 0
    % already ended with newline above
end
end
