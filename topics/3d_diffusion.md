# 3D Diffusion Model
- arXiv 2023.08, **Diffusion with Forward Models**: Solving Stochastic Inverse Problems Without Direct Supervision, [Website](https://diffusion-with-forward-models.github.io/)
- arXiv 2023.07, **NIFTY**: Neural Object Interaction Fields for Guided Human Motion Synthesis, [Website](https://nileshkulkarni.github.io/nifty/)
- arXiv 2023.03, Let 2D Diffusion Model Know 3D-Consistency for Robust Text-to-3D Generation, [arXiv](https://arxiv.org/abs/2303.07937) / [GitHub](https://github.com/KU-CVLAB/3DFuse) / [Website](https://ku-cvlab.github.io/3DFuse/)
  - main intuition is to incorporate 3D information into 2D diffusion model
  - and still, use 2D diffusion model to optimize nerf
- ICLR 2023 outstanding paper award, **DreamFusion**: Text-to-3D using 2D Diffusion, [OpenReview](https://openreview.net/forum?id=FjNys5c7VyY)
- NIPS 2022, **LION**: Latent Point Diffusion Models for 3D Shape Generation, [Website](https://nv-tlabs.github.io/LION/)
- CVPR 2022, Zero-Shot Text-Guided Object
Generation with Dream Fields, [Website](https://ajayj.com/dreamfields) / [GitHub](https://github.com/google-research/google-research/tree/master/dreamfields)
- arXiv 2022.12, **Point-E**: A System for Generating 3D Point Clouds from Complex Prompts, [arXiv](https://arxiv.org/abs/2212.08751) / [GitHub](https://github.com/openai/point-e)
  - text -> image -> point cloud
  - use transformer to generate point cloud
  - point cloud diffusion not condition on language
- arXiv 2022.11, **NFD**: 3D Neural Field Generation using Triplane Diffusion, [arXiv](https://arxiv.org/abs/2211.16677) / [Website](https://jryanshue.com/nfd/)
  - two-stage model
  - use 2D diffusion model to generate three planes
  - use occupancy network to generate 3D point cloud based on three plane interpolation
- arXiv 2022.08, **3DiM**: Novel View Synthesis with Diffusion Models, [Website](https://3d-diffusion.github.io/)

