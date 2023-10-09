# Diffusion Model

## Controllable
- ICCV 2023, Unsupervised Compositional Concepts Discovery with Text-to-Image Generative Models, [Website](https://energy-based-model.github.io/unsupervised-concept-discovery/)
- arXiv 2023.02, **ControlNet**: Adding Conditional Control to Text-to-Image Diffusion Models, [arXiv](https://arxiv.org/abs/2302.05543) / [Github](https://github.com/lllyasviel/ControlNet)
- CVPR 2023, **DreamBooth**: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation, [Website](https://dreambooth.github.io/)
- ICLR 2023, **Prompt-to-Prompt** Image Editing with Cross-Attention Control, [arXiv](https://arxiv.org/abs/2208.01626) / [Website](https://prompt-to-prompt.github.io)
- ICLR 2023, An Image is Worth One Word: Personalizing Text-to-Image Generation using **Textual Inversion**, [Website](https://textual-inversion.github.io/)

## Applications
- ICLR 2023, **MDM**: Human Motion Diffusion Model, [Website](https://guytevet.github.io/mdm-page/)
- arXiv 2022.05, Diffusion-LM Improves Controllable Text Generation, [arXiv](https://arxiv.org/abs/2205.14217)


## High Resolution
- arXiv 2022.10, **Imagen Video**: High Definition Video Generation with Diffusion Models, [arXiv](https://arxiv.org/abs/2210.02303) / [Website](https://imagen.research.google/video/)
- NIPS 2022, **k-diffusion**: Elucidating the Design Space of Diffusion-Based Generative Models, [arXiv](https://arxiv.org/abs/2206.00364) / [Github](https://github.com/crowsonkb/k-diffusion)
- CVPR 2022, **Stable Diffusion**: High-Resolution Image Synthesis with Latent Diffusion Models, [arXiv](https://arxiv.org/abs/2112.10752)
- NIPS 2022, **Imagen**: Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding, [arXiv](https://arxiv.org/abs/2205.11487)
- arXiv 2022.07, Classifier-Free Diffusion Guidance, [arXiv](https://arxiv.org/abs/2207.12598)
- NIPS 2021, **Guided Diffusion**: Diffusion Models Beat GANS on Image Synthesis, [arXiv](https://arxiv.org/abs/2105.05233) / [Github](https://github.com/openai/guided-diffusion)

- ICLR 2021, Score-Based Generative Modeling through Stochastic Differential Equations, [arXiv](https://arxiv.org/abs/2011.13456)
- ICML 2021, **iDDPM**: Improved Denoising Diffusion Probabilistic Models, [arXiv](https://arxiv.org/abs/2102.09672) / [Github](https://github.com/openai/improved-diffusion)
- NIPS 2020, **DDPM**: Denoising Diffusion Probabilistic Models, [Website](https://hojonathanho.github.io/diffusion/)


## Feature Utilization
- arXiv 2023.06, Emergent Correspondence from Image Diffusion, [Website](https://diffusionfeatures.github.io/)
- CVPR 2023, **ODISE**: Open-Vocabulary Panoptic Segmentation with Text-to-Image Diffusion Models, [Website](https://jerryxu.net/ODISE/)

## Sampling
- ICLR 2023 spotlight, **gDDIM**: Generalized denoising diffusion implicit models, [arXiv](https://arxiv.org/abs/2206.05564)
- ICLR 2023, **DEIS**: Fast Sampling of Diffusion Models with Exponential Integrator, [arXiv](https://arxiv.org/abs/2204.13902) / [Github](https://github.com/qsh-zh/deis)
- ICLR 2022, Progressive Distillation for Fast Sampling of Diffusion Models, [Openreview](https://openreview.net/forum?id=TIdIXIpzhoI) / [Github](https://github.com/google-research/google-research/tree/master/diffusion_distillation)
- ICLR 2022 outstanding paper award, **Analytic-DPM**: an Analytic Estimate of the Optimal Reverse Variance in Diffusion Probabilistic Models
, [arXiv](https://arxiv.org/abs/2201.06503)
- NeurIPS 2022 oral, **DPM-Solver**: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps
, [arXiv](https://arxiv.org/abs/2206.00927)
- ICLR 2021, **DDIM**: Denoising Diffusion Implicit Models, [arXiv](https://arxiv.org/abs/2010.02502) / [Github](https://github.com/ermongroup/ddim)

  
## 3D
- CoRL 2023, **ChainedDiffuser**: Unifying Diffusion Models with Action Detection Transformers for Multi-task Robotic Manipulation, [OpenReview](https://openreview.net/pdf?id=W0zgY2mBTA8)
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

