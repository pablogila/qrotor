

B = 1;
ω=1;
V =0;
U[x_]:=V (1-Cos[3 x])/2;
Plot[U[x],{x,0,2π}X]
solutions=NDEigensystem[{-B ψ''[x]+U[x] ψ[x],ψ[0]==ψ[2 π]},ψ,{x,0,2 π},8]
energies = solutions[[1]];
entrans1 = {(energies[[2]] - energies[[1]])*0.655}
entrans2 = {(energies[[4]] - energies[[2]])*0.655}
Vlist = {V*0.655};
eigenvalues = energies;
While[V<50, V = V+0.1; Vlist = Join[Vlist, {V*0.655}];
solutions=NDEigensystem[{-B ψ''[x]+U[x] ψ[x],ψ[0]==ψ[2 π]},ψ,{x,0,2 π},8]; energies = solutions[[1]];
transone = (energies[[2]] - energies[[1]])*0.655; transtwo = (energies[[4]] - energies[[2]])*0.655;
entrans1 = Join[entrans1, {transone}];entrans2 = Join[entrans2, {transtwo}];
eigenvalues = Join[eigenvalues, energies];];
entransfer1matrix = {Vlist,entrans1};
entransfer2matrix = {Vlist,entrans2};
eigenvaluesmatrix = Partition[eigenvalues,8];
ListPlot[entrans1]
ListPlot[entrans2]
Export["entr1.mat", entransfer1matrix]
Export["entr2.mat", entransfer2matrix]
Export["eigenvalues.mat", eigenvaluesmatrix]