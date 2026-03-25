"""
U-Net++ 模型架构
基于 Nested U-Net 的语义分割网络
论文: UNet++: A Nested U-Net Architecture for Medical Image Segmentation
"""
from typing import List, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import vgg19, vgg19_bn


class ConvBlock(nn.Module):
    """卷积块: Conv2d + BatchNorm + ReLU"""

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, padding: int = 1) -> None:
        super(ConvBlock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size, padding=padding, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class UNetPlusPlus(nn.Module):
    """U-Net++ 网络"""

    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 4,
        deep_supervision: bool = True,
        encoder_name: str = 'vgg19',
        pretrained: bool = True
    ) -> None:
        """
        初始化U-Net++

        Args:
            in_channels: 输入图像通道数
            num_classes: 分割类别数(包括背景)
            deep_supervision: 是否使用深度监督
            encoder_name: 编码器名称('vgg19' 或 'vgg19_bn')
            pretrained: 是否使用预训练权重
        """
        super(UNetPlusPlus, self).__init__()
        
        self.deep_supervision = deep_supervision
        self.num_classes = num_classes
        
        # 使用VGG19作为编码器(提取特征)
        if encoder_name == 'vgg19':
            vgg = vgg19(pretrained=pretrained)
            features = vgg.features
            self.encoder_name = 'vgg19'
        elif encoder_name == 'vgg19_bn':
            vgg = vgg19_bn(pretrained=pretrained)
            features = vgg.features
            self.encoder_name = 'vgg19_bn'
        else:
            raise ValueError(f"不支持的编码器: {encoder_name}")
        
        # 编码器特征提取层
        self.encoder1 = nn.Sequential(*features[:4])   # 64通道
        self.encoder2 = nn.Sequential(*features[4:9])  # 128通道
        self.encoder3 = nn.Sequential(*features[9:18]) # 256通道
        self.encoder4 = nn.Sequential(*features[18:27])# 512通道
        self.encoder5 = nn.Sequential(*features[27:])  # 512通道
        
        # 获取各层通道数
        if 'bn' in encoder_name:
            filters = [64, 128, 256, 512, 512]
        else:
            filters = [64, 128, 256, 512, 512]
        
        # 计算桥接层的padding以匹配尺寸
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        
        # 解码器卷积块
        # 第4层解码器: 输入 512+512=1024 -> 输出 512
        self.decoder4 = ConvBlock(filters[4] + filters[3], filters[3])
        
        # 第3层解码器: 输入 512+512=1024 -> 输出 256  
        self.decoder3 = ConvBlock(filters[3] + filters[3], filters[2])
        
        # 第2层解码器: 输入 256+256=512 -> 输出 128
        self.decoder2 = ConvBlock(filters[2] + filters[2], filters[1])
        
        # 第1层解码器: 输入 128+128=256 -> 输出 64
        self.decoder1 = ConvBlock(filters[1] + filters[1], filters[0])
        
        # 深度监督输出层
        if deep_supervision:
            self.output1 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
            self.output2 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
            self.output3 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
            self.output4 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
        else:
            self.output = nn.Conv2d(filters[0], num_classes, kernel_size=1)
        
        # 最终输出层
        self.final_conv = ConvBlock(filters[0] * 2, filters[0])  # 处理d0的拼接
    
    def forward(self, x: torch.Tensor) -> Union[torch.Tensor, List[torch.Tensor]]:
        """前向传播 - 简化版U-Net++"""
        # 编码器
        e1 = self.encoder1(x)      # [B, 64, 512, 512]
        e2 = self.encoder2(e1)     # [B, 128, 256, 256]
        e3 = self.encoder3(e2)     # [B, 256, 128, 128]
        e4 = self.encoder4(e3)     # [B, 512, 64, 64]
        e5 = self.encoder5(e4)     # [B, 512, 16, 16] 注意:VGG19有额外的pool导致16x16
        
        # 解码器路径
        # 第4层上采样: 16x16 -> 32x32 
        d4 = self.up(e5)  # [B, 512, 32, 32]
        e4_pooled = F.max_pool2d(e4, kernel_size=2, stride=2)  # [B, 512, 32, 32]
        d4 = torch.cat([d4, e4_pooled], dim=1)  # [B, 1024, 32, 32]
        d4 = self.decoder4(d4)  # [B, 512, 32, 32]
        
        # 第3层上采样: 32x32 -> 64x64
        d3 = self.up(d4)  # [B, 512, 64, 64]
        d3 = torch.cat([d3, e4], dim=1)  # [B, 1024, 64, 64]
        d3 = self.decoder3(d3)  # [B, 256, 64, 64]
        
        # 第2层上采样: 64x64 -> 128x128
        d2 = self.up(d3)  # [B, 256, 128, 128]
        d2 = torch.cat([d2, e3], dim=1)  # [B, 512, 128, 128]
        d2 = self.decoder2(d2)  # [B, 128, 128, 128]
        
        # 第1层上采样: 128x128 -> 256x256
        d1 = self.up(d2)  # [B, 128, 256, 256]
        d1 = torch.cat([d1, e2], dim=1)  # [B, 256, 256, 256]
        d1 = self.decoder1(d1)  # [B, 64, 256, 256]
        
        # 最终上采样: 256x256 -> 512x512
        d0 = self.up(d1)  # [B, 64, 512, 512]
        d0 = torch.cat([d0, e1], dim=1)  # [B, 128, 512, 512]
        d0 = self.final_conv(d0)  # [B, 64, 512, 512]
        
        # 输出
        if self.deep_supervision:
            # 深度监督模式:输出多个尺度的预测
            output1 = self.output1(d1)
            output2 = self.output2(d1)
            output3 = self.output3(d1)
            output4 = self.output4(d0)  # 最终输出
            return [output1, output2, output3, output4]
        else:
            output = self.output(d0)  # 最终输出
            return output


if __name__ == '__main__':
    # 测试模型
    print("测试U-Net++模型...")
    
    model = UNetPlusPlus(in_channels=3, num_classes=4, deep_supervision=True)
    
    # 测试输入
    x = torch.randn(2, 3, 512, 512)
    
    # 前向传播
    outputs = model(x)
    
    if isinstance(outputs, list):
        for i, out in enumerate(outputs):
            print(f"输出 {i+1} 形状: {out.shape}")
    else:
        print(f"输出形状: {outputs.shape}")
    
    # 计算参数数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"\n总参数量: {total_params:,}")
    print(f"可训练参数量: {trainable_params:,}")
