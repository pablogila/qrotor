import qrotor as qr
import os
import shutil


gridsizes = {1000: '10G', 2000: '10G', 3000: '10G', 5000: '10G', 10000: '20G', 15000: '20G', 20000: '20G', 30000: '50G', 40000: '50G', 50000: '50G', 60000: '100G', 70000: '100G', 80000: '200G', 90000: '300G', 100000: '400G', 125000: '500G', 150000: '700G', 175000: '1000G', 200000: '1000G', 250000: '2000G', 300000: '2000G'}

script_name = 'convergence_job.py'
script_file = os.path.join(os.getcwd(), script_name)

slurm_name = 'convergence.slurm'
slurm_file = os.path.join(os.getcwd(), slurm_name)

for gridsize, memory in gridsizes.items():
    slurm_copy_name = f'temp_{gridsize}.slurm'
    slurm_copy = os.path.join(os.getcwd(), slurm_copy_name)
    shutil.copy(slurm_file, slurm_copy)

    script_copy_name = f'temp_{gridsize}.py'
    script_copy = os.path.join(os.getcwd(), script_copy_name)
    shutil.copy(script_file, script_copy)

    qr.file.replace_line_with_keyword(f'#SBATCH --job-name=QRotor_{gridsize}', '#SBATCH --job-name=', slurm_copy)
    qr.file.replace_line_with_keyword(f'#SBATCH --mem={memory}', '#SBATCH --mem=', slurm_copy)
    qr.file.replace_line_with_keyword(f'python3 {script_copy_name}', 'python3 ', slurm_copy)

    qr.file.replace_line_with_keyword(f'this_script_is_a_copy=True', 'this_script_is_a_copy=', script_copy)
    qr.file.replace_line_with_keyword(f'gridsize={gridsize}', 'gridsize=', script_copy)
    qr.file.replace_line_with_keyword(f'slurm_file="{slurm_copy}"', 'slurm_file=', script_copy)
    
    os.system(f'python3 {script_copy_name}')  # DEBUG
    #os.system(f'sbatch {slurm_copy_name}')
    print(f'Sbatched {slurm_copy_name}...')

