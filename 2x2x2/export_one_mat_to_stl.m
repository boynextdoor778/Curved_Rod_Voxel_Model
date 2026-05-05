function export_one_mat_to_stl(matFile, stlFile, voxelSize)
% EXPORT_ONE_MAT_TO_STL Convert one MAT voxel file to binary STL.

if nargin < 3 || isempty(voxelSize)
    voxelSize = [1 1 1];
end

S = load(matFile);
if ~isfield(S, 'voxel')
    error('MAT file does not contain variable "voxel": %s', matFile);
end

voxel = logical(S.voxel);
export_voxel_to_stl_binary(voxel, stlFile, voxelSize);

fprintf('STL exported: %s\n', stlFile);
end
