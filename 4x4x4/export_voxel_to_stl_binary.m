function export_voxel_to_stl_binary(voxel, stlFile, voxelSize)
% EXPORT_VOXEL_TO_STL_BINARY Export a logical voxel volume to binary STL.

if nargin < 3 || isempty(voxelSize)
    voxelSize = [1 1 1];
end

voxel = logical(voxel);
if ~any(voxel(:))
    error('Voxel model is empty.');
end

% Pad by one empty voxel to close boundary surfaces.
voxelPad = padarray(voxel, [1 1 1], 0, 'both');
fv = isosurface(double(voxelPad), 0.5);

if isempty(fv.faces) || isempty(fv.vertices)
    error('Empty isosurface generated.');
end

% Convert matrix-grid coordinates to physical coordinates.
fv.vertices(:,1) = (fv.vertices(:,1) - 1) * voxelSize(1);
fv.vertices(:,2) = (fv.vertices(:,2) - 1) * voxelSize(2);
fv.vertices(:,3) = (fv.vertices(:,3) - 1) * voxelSize(3);

write_binary_stl(stlFile, fv.faces, fv.vertices);
end

function write_binary_stl(filename, faces, vertices)
fid = fopen(filename, 'w');
if fid == -1
    error('Cannot open STL file for writing: %s', filename);
end
cleaner = onCleanup(@() fclose(fid)); %#ok<NASGU>

header = uint8(zeros(1, 80));
label = uint8('Voxel lattice STL generated from MATLAB');
header(1:numel(label)) = label;
fwrite(fid, header, 'uint8');
fwrite(fid, uint32(size(faces,1)), 'uint32');

for i = 1:size(faces,1)
    v1 = vertices(faces(i,1), :);
    v2 = vertices(faces(i,2), :);
    v3 = vertices(faces(i,3), :);

    n = cross(v2 - v1, v3 - v1);
    nn = norm(n);
    if nn > 0
        n = n / nn;
    else
        n = [0 0 0];
    end

    fwrite(fid, single(n), 'float32');
    fwrite(fid, single(v1), 'float32');
    fwrite(fid, single(v2), 'float32');
    fwrite(fid, single(v3), 'float32');
    fwrite(fid, uint16(0), 'uint16');
end
end
