running command
./scripts/run_inference.py inference.input_pdb=xxx 'contigmap.contigs=[A1-166/0 190-190]' 'ppi.hotspot_res=[xxx]' inference.num_designs=100 denoiser.noise_scale_ca=0.5 denoiser.noise_scale_frame=0 \
  inference.output_prefix=/home/eric/proj/RFdiffusion/xxx \
  dfire.enable=true \
  dfire.total_res=300 \
  dfire.eval_every=20 \
  dfire.target=0.92 \
  dfire.max_mult=3.0 \
  dfire.min_scale=0.1 \
  dfire.script=/home/eric/proj/RFdiffusion/tools/dfire2_once.py \
  dfire.cmd_prefix='conda run -n lightdock'

rfdiffusion installation reference:https://github.com/RosettaCommons/RFdiffusion.git


lightdock installation reference:https://github.com/lightdock/lightdock.git
