function save_sample_mat(matFile, voxel, density, radius, bendAmp, nPtsPerArm, refAxis, nVoxel, topoFile)
% Save one accepted sample from parfor safely.
voxel = logical(voxel);
save(matFile, 'voxel', 'density', 'radius', 'bendAmp', ...
    'nPtsPerArm', 'refAxis', 'nVoxel', 'topoFile');
end
