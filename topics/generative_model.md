# Generative Model
- [Generative Model](#generative-model)
  - [3D Diffusion Model](#3d-diffusion-model)
  - [Diffusion Model](#diffusion-model)
  - [Diffusion Model Application](#diffusion-model-application)
  - [Generative Adversarial Networks](#generative-adversarial-networks)

## 3D Diffusion Model
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



## Diffusion Model
- arXiv 2023, ControlNet: Adding Conditional Control to Text-to-Image Diffusion Models, [arXiv](https://arxiv.org/abs/2302.05543)
- CVPR 2022, Stable Diffusion: High-Resolution Image Synthesis with Latent Diffusion Models, [arXiv](https://arxiv.org/abs/2112.10752)
- NIPS 2022, Imagen: Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding, [arXiv](https://arxiv.org/abs/2205.11487)
- NIPS 2021, Guided Diffusion: Diffusion Models Beat GANS on Image Synthesis, [arXiv](https://arxiv.org/abs/2105.05233)
- NIPS 2020, DDPM: Denoising Diffusion Probabilistic Models, [Website](https://hojonathanho.github.io/diffusion/)



## Diffusion Model Application
- CVPR 2023, ODISE: Open-Vocabulary Panoptic Segmentation with Text-to-Image Diffusion Models, [Website](https://jerryxu.net/ODISE/)


## Generative Adversarial Networks
- NIPS 2022, GET3D: A Generative Model of High Quality 3D Textured Shapes Learned from Images, [Website](https://nv-tlabs.github.io/GET3D/)
- CVPR 2022, EG3D: Efficient Geometry-aware 3D Generative Adversarial Networks, [Website](https://nvlabs.github.io/eg3d/)
- arXiv 2022, Learning to Learn with Generative Models of Neural Network Checkpoints, [Website](https://www.wpeebles.com/Gpt)
- CVPR 2021 oral, VQGAN: Taming Transformers for High-Resolution Image Synthesis, [Website](https://compvis.github.io/taming-transformers/)
- CVPR 2021, Closed-Form Factorization of Latent Semantics in GANs, [Website](https://genforce.github.io/sefa/)
- CVPR 2019, StyleGAN: A Style-Based Generator Architecture for Generative Adversarial Networks, [arXiv](https://arxiv.org/abs/1812.04948)


