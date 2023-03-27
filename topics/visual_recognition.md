# Visual Recognition

- [Visual Recognition](#visual-recognition)
  - [Detection](#detection)
  - [Segmentation](#segmentation)
  - [Pose Estimation](#pose-estimation)
  - [Architecture](#architecture)
  - [Loss Function](#loss-function)



## Detection
- ECCV 2022, Detic: [Detecting Twenty-thousand Classes using Image-level Supervision](https://github.com/facebookresearch/Detic)
  - Detects any class given class names (using CLIP).
  - We train the detector on ImageNet-21K dataset with 21K classes.
  - Cross-dataset generalization to OpenImages and Objects365 without finetuning.
  - State-of-the-art results on Open-vocabulary LVIS and Open-vocabulary COCO.
- CVPR 2020 oral, Hand Object Detector: [Understanding Human Hands in Contact at Internet Scale](https://fouheylab.eecs.umich.edu/~dandans/projects/100DOH/)


## Segmentation
- ICLR 2023 oral, [Image as Set of Points](https://openreview.net/forum?id=awnvqZja69)
- CVPR 2023, [Open-Vocabulary Panoptic Segmentation with Text-to-Image Diffusion Models](https://jerryxu.net/ODISE/)
- ICLR 2022, LSeg: [Language-driven Semantic Segmentation](https://arxiv.org/abs/2201.03546)
  - use CLIP for semantic segmentation. generalizable!
  - produce per-pixel embedding (this is nice)
- CVPR 2022, [Masked-attention Mask Transformer for Universal Image Segmentation](https://bowenc0221.github.io/mask2former/)

## Pose Estimation
- ICLR 2023, [Self-Supervised Geometric Correspondence for Category-Level 6D Object Pose Estimation in the Wild](https://kywind.github.io/self-pose)
- CVPR 2019, NOCS: [Normalized Object Coordinate Space for Category-Level 6D Object Pose and Size Estimation](https://arxiv.org/abs/1901.02970)
- CVPR 2022, [Human Hands as Probes for Interactive Object Understanding](https://s-gupta.github.io/hands-as-probes/)
- arXiv 2021, [FrankMocap: A Monocular 3D Whole-Body Pose Estimation System via Regression and Integration](https://arxiv.org/abs/2108.06428)
- NIPS 2021, TTP: [Test-Time Personalization with a Transformer for Human Pose Estimation](http://liyizhuo.com/TTP/)
- CVPR 2019 oral, [3D Hand Shape and Pose Estimation from a Single RGB Image](https://sites.google.com/site/geliuhaontu/home/cvpr2019)
  - they have code and pretrain model: [here](https://github.com/3d-hand-shape/hand-graph-cnn)
  - use graph CNN to get hand vertices
- CVPR 2021, [Semi-Supervised 3D Hand-Object Poses Estimation with Interactions in Time](https://stevenlsw.github.io/Semi-Hand-Object/)


## Architecture
- ICLR 2022, [Perceiver IO: A General Architecture for Structured Inputs & Outputs](https://arxiv.org/abs/2107.14795)
- ICML 2021, [Perceiver: General Perception with Iterative Attention](https://arxiv.org/abs/2103.03206)
- ICLR 2021, Vision Transformer: [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929)
- ICCV 2019, [Rethinking ImageNet Pre-Training](https://openaccess.thecvf.com/content_ICCV_2019/html/He_Rethinking_ImageNet_Pre-Training_ICCV_2019_paper.html)
- NIPS 2017, SELU: [Self-Normalizing Neural Networks](https://arxiv.org/abs/1706.02515)

## Loss Function
- ECCV 2016, [Perceptual Losses for Real-Time Style Transfer and Super-Resolution](https://arxiv.org/abs/1603.08155)


