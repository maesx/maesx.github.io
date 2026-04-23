"""
U-Net++ 增强版本 - 集成多种注意力机制
支持 CBAM, SE, ASPP 等注意力模块
"""
from typing import List, Union
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import vgg19, vgg19_bn

from .attention_modules import CBAM, SEBlock, ASPP


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


class UNetPlusPlusEnhanced(nn.Module):
    """
    U-Net++ 增强版本
    集成注意力机制以提升分割性能
    
    支持的注意力类型:
    - 'none': 原始U-Net++ (基线)
    - 'cbam': Channel & Spatial Attention
    - 'se': Squeeze-and-Excitation
    - 'aspp': Atrous Spatial Pyramid Pooling
    - 'cbam_aspp': CBAM + ASPP组合
    - 'se_aspp': SE + ASPP组合
    - 'full': SE (编码器) + ASPP (瓶颈) + CBAM (解码器)
    """
    
    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 4,
        deep_supervision: bool = True,
        encoder_name: str = 'vgg19',
        pretrained: bool = True,
        attention_type: str = 'cbam'
    ) -> None:
        """
        Args:
            in_channels: 输入图像通道数
            num_classes: 分割类别数(包括背景)
            deep_supervision: 是否使用深度监督
            encoder_name: 编码器名称('vgg19' 或 'vgg19_bn')
            pretrained: 是否使用预训练权重
            attention_type: 注意力类型 ('none', 'cbam', 'se', 'aspp', 'cbam_aspp', 'se_aspp', 'full')
        """
        super(UNetPlusPlusEnhanced, self).__init__()
        
        self.deep_supervision = deep_supervision
        self.num_classes = num_classes
        self.attention_type = attention_type
        
        # 使用VGG19作为编码器
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
        
        # 通道数配置
        filters = [64, 128, 256, 512, 512]
        
        # 根据注意力类型添加注意力模块
        self._setup_attention_modules(filters, attention_type)
        
        # 池化和上采样
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        
        # 解码器卷积块
        self.decoder4 = ConvBlock(filters[4] + filters[3], filters[3])
        self.decoder3 = ConvBlock(filters[3] + filters[3], filters[2])
        self.decoder2 = ConvBlock(filters[2] + filters[2], filters[1])
        self.decoder1 = ConvBlock(filters[1] + filters[1], filters[0])
        
        # 最终输出层
        self.final_conv = ConvBlock(filters[0] * 2, filters[0])
        
        # 深度监督输出层
        if deep_supervision:
            self.output1 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
            self.output2 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
            self.output3 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
            self.output4 = nn.Conv2d(filters[0], num_classes, kernel_size=1)
        else:
            self.output = nn.Conv2d(filters[0], num_classes, kernel_size=1)
    
    def _setup_attention_modules(self, filters: list, attention_type: str) -> None:
        """根据注意力类型设置注意力模块"""
        
        # 编码器注意力
        if attention_type in ['cbam', 'cbam_aspp', 'full']:
            # CBAM在编码器
            self.cbam_e1 = CBAM(filters[0])
            self.cbam_e2 = CBAM(filters[1])
            self.cbam_e3 = CBAM(filters[2])
            self.cbam_e4 = CBAM(filters[3])
            self.cbam_e5 = CBAM(filters[4])
        
        if attention_type in ['se', 'se_aspp', 'full']:
            # SE在编码器
            self.se_e1 = SEBlock(filters[0])
            self.se_e2 = SEBlock(filters[1])
            self.se_e3 = SEBlock(filters[2])
            self.se_e4 = SEBlock(filters[3])
            self.se_e5 = SEBlock(filters[4])
        
        # ASPP在瓶颈层
        if attention_type in ['aspp', 'cbam_aspp', 'se_aspp', 'full']:
            self.aspp = ASPP(filters[4], filters[4])
        
        # 解码器注意力 (CBAM)
        if attention_type in ['cbam', 'cbam_aspp', 'full']:
            self.cbam_d4 = CBAM(filters[3])
            self.cbam_d3 = CBAM(filters[2])
            self.cbam_d2 = CBAM(filters[1])
            self.cbam_d1 = CBAM(filters[0])
    
    def _apply_encoder_attention(self, e: torch.Tensor, layer_idx: int) -> torch.Tensor:
        """应用编码器注意力"""
        if self.attention_type in ['cbam', 'cbam_aspp', 'full']:
            cbam_modules = [self.cbam_e1, self.cbam_e2, self.cbam_e3, self.cbam_e4, self.cbam_e5]
            e = cbam_modules[layer_idx](e)
        
        if self.attention_type in ['se', 'se_aspp', 'full']:
            se_modules = [self.se_e1, self.se_e2, self.se_e3, self.se_e4, self.se_e5]
            e = se_modules[layer_idx](e)
        
        return e
    
    def _apply_decoder_attention(self, d: torch.Tensor, layer_idx: int) -> torch.Tensor:
        """应用解码器注意力"""
        if self.attention_type in ['cbam', 'cbam_aspp', 'full']:
            cbam_modules = [self.cbam_d1, self.cbam_d2, self.cbam_d3, self.cbam_d4]
            d = cbam_modules[layer_idx](d)
        
        return d
    
    def forward(self, x: torch.Tensor) -> Union[torch.Tensor, List[torch.Tensor]]:
        """前向传播"""
        # 编码器路径
        e1 = self.encoder1(x)                        # [B, 64, 512, 512]
        e1 = self._apply_encoder_attention(e1, 0)
        
        e2 = self.encoder2(e1)                       # [B, 128, 256, 256]
        e2 = self._apply_encoder_attention(e2, 1)
        
        e3 = self.encoder3(e2)                       # [B, 256, 128, 128]
        e3 = self._apply_encoder_attention(e3, 2)
        
        e4 = self.encoder4(e3)                       # [B, 512, 64, 64]
        e4 = self._apply_encoder_attention(e4, 3)
        
        e5 = self.encoder5(e4)                       # [B, 512, 16, 16]
        e5 = self._apply_encoder_attention(e5, 4)
        
        # 应用ASPP (如果启用)
        if self.attention_type in ['aspp', 'cbam_aspp', 'se_aspp', 'full']:
            e5 = self.aspp(e5)
        
        # 解码器路径
        # 第4层上采样: 16x16 -> 32x32
        d4 = self.up(e5)
        e4_pooled = F.max_pool2d(e4, kernel_size=2, stride=2)
        d4 = torch.cat([d4, e4_pooled], dim=1)
        d4 = self.decoder4(d4)
        d4 = self._apply_decoder_attention(d4, 3)
        
        # 第3层上采样: 32x32 -> 64x64
        d3 = self.up(d4)
        d3 = torch.cat([d3, e4], dim=1)
        d3 = self.decoder3(d3)
        d3 = self._apply_decoder_attention(d3, 2)
        
        # 第2层上采样: 64x64 -> 128x128
        d2 = self.up(d3)
        d2 = torch.cat([d2, e3], dim=1)
        d2 = self.decoder2(d2)
        d2 = self._apply_decoder_attention(d2, 1)
        
        # 第1层上采样: 128x128 -> 256x256
        d1 = self.up(d2)
        d1 = torch.cat([d1, e2], dim=1)
        d1 = self.decoder1(d1)
        d1 = self._apply_decoder_attention(d1, 0)
        
        # 最终上采样: 256x256 -> 512x512
        d0 = self.up(d1)
        d0 = torch.cat([d0, e1], dim=1)
        d0 = self.final_conv(d0)
        
        # 输出
        if self.deep_supervision:
            output1 = self.output1(d1)
            output2 = self.output2(d1)
            output3 = self.output3(d1)
            output4 = self.output4(d0)
            return [output1, output2, output3, output4]
        else:
            output = self.output(d0)
            return output


def create_model(
    num_classes: int = 4,
    attention_type: str = 'cbam',
    encoder_name: str = 'vgg19',
    pretrained: bool = True,
    deep_supervision: bool = True
) -> UNetPlusPlusEnhanced:
    """
    创建U-Net++增强模型的工厂函数
    
    Args:
        num_classes: 分割类别数
        attention_type: 注意力类型
        encoder_name: 编码器名称
        pretrained: 是否使用预训练权重
        deep_supervision: 是否使用深度监督
    
    Returns:
        配置好的模型实例
    """
    return UNetPlusPlusEnhanced(
        in_channels=3,
        num_classes=num_classes,
        deep_supervision=deep_supervision,
        encoder_name=encoder_name,
        pretrained=pretrained,
        attention_type=attention_type
    )


if __name__ == '__main__':
    # 测试模型
    print("测试U-Net++增强版...")
    
    # 测试不同注意力类型
    attention_types = ['none', 'cbam', 'se', 'aspp', 'cbam_aspp', 'full']
    
    for attn_type in attention_types:
        print(f"\n{'='*60}")
        print(f"测试注意力类型: {attn_type}")
        print('='*60)
        
        model = create_model(
            num_classes=4,
            attention_type=attn_type,
            encoder_name='vgg19',
            pretrained=False
        )
        
        # 测试前向传播
        x = torch.randn(2, 3, 512, 512)
        outputs = model(x)
        
        if isinstance(outputs, list):
            print(f"深度监督输出: {[out.shape for out in outputs]}")
        else:
            print(f"输出形状: {outputs.shape}")
        
        # 计算参数量
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"总参数量: {total_params:,}")
        print(f"可训练参数量: {trainable_params:,}")
        print(f"模型大小: {total_params * 4 / 1024 / 1024:.2f} MB")
