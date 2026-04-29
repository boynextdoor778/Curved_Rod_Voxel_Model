function save_repeat444_mat(repFile, voxel, repeatN, S)
% Save repeated 4x4x4 MAT safely for parfor

saveVars = struct();
saveVars.voxel = voxel;
saveVars.repeatN = repeatN;

metaList = {'density','radius','bendAmp','nPtsPerArm','refAxis','nVoxel','topoFile'};
for k = 1:numel(metaList)
    name = metaList{k};
    if isfield(S, name)
        saveVars.(name) = S.(name);
    end
end

save(repFile, '-struct', 'saveVars');
end