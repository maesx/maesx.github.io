"""
极致优化版 U-Net++ - 目标 IoU 80%
采用 ResNet-101 编码器 + 多尺度特征融合 + 边界优化

主要改进:
1. ResNet-101 编码器 (比VGG19更强,残差连接)
2. 特征金字塔网络 (FPN) 多尺度融合
3. 深度可分离卷积 (减少参数)
4. 边界监督模块 (提升边界精度)
5. 更强的注意力机制组合
"""
from typing import List, Union, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet101, ResNet101_Weights

from .attention_modules import CBAM, SEBlock, ASPP


class ConvBNReLU(nn.Module):
    """卷积 + BatchNorm + ReLU"""
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        padding: int = 1,
        stride: int = 1,
        groups: int = 1,
        use_separable: bool = False
    ) -> None:
        super(ConvBNReLU, self).__init__()
        
        if use_separable:
            # 深度可分离卷积
            self.conv = nn.Sequential(
                # 深度卷积
                nn.Conv2d(in_channels, in_channels, kernel_size,
                         stride=stride, padding=padding, groups=in_channels, bias=False),
                nn.BatchNorm2d(in_channels),
                # 逐点卷积
                nn.Conv2d(in_channels, out_channels, 1, bias=False),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(inplace=True)
            )
        else:
            self.conv = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size,
                         stride=stride, padding=padding, groups=groups, bias=False),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(inplace=True)
            )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class BoundaryRefinementModule(nn.Module):
    """
    边界优化模块
    通过边缘监督提升分割边界精度
    """
    def __init__(self, in_channels: int, num_classes: int) -> None:
        super(BoundaryRefinementModule, self).__init__()
        
        # 边界检测分支
        self.boundary_conv = nn.Sequential(
            ConvBNReLU(in_channels, in_channels // 4, 3),
            ConvBNReLU(in_channels // 4, in_channels // 4, 3),
            nn.Conv2d(in_channels // 4, 1, 1)
        )
        
        # 特征精炼
        self.refine_conv = ConvBNReLU(in_channels + 1, in_channels, 3)
        
    def forward(self, x: torch.Tensor) -> tuple:
        """
        Returns:
            x_refined: 精炼后的特征
            boundary: 边界预测
        """
        boundary = self.boundary_conv(x)
        x_cat = torch.cat([x, boundary], dim=1)
        x_refined = self.refine_conv(x_cat)
        return x_refined, boundary


class FeaturePyramidNetwork(nn.Module):
    """
    特征金字塔网络 (FPN)
    自顶向下融合多尺度特征
    """
    def __init__(self, in_channels_list: List[int], out_channels: int = 256) -> None:
        super(FeaturePyramidNetwork, self).__init__()
        
        # 横向连接 (1x1卷积降维)
        self.lateral_convs = nn.ModuleList([
            nn.Conv2d(in_ch, out_channels, 1)
            for in_ch in in_channels_list
        ])
        
        # 平滑卷积
        self.smooth_convs = nn.ModuleList([
            ConvBNReLU(out_channels, out_channels, 3)
            for _ in in_channels_list
        ])
        
    def forward(self, features: List[torch.Tensor]) -> List[torch.Tensor]:
        """
        Args:
            features: 从低层到高层的特征列表 [C2, C3, C4, C5]
        
        Returns:
            fpn_features: FPN特征列表 [P2, P3, P4, P5]
        """
        # 自顶向下路径
        fpn_features = []
        
        # 最高层特征
        fpn_features.append(self.lateral_convs[-1](features[-1]))
        
        # 自顶向下融合
        for i in range(len(features) - 2, -1, -1):
            # 上采样高层特征
            upsampled = F.interpolate(
                fpn_features[-1],
                size=features[i].shape[-2:],
                mode='bilinear',
                align_corners=True
            )
            # 横向连接
            lateral = self.lateral_convs[i](features[i])
            # 融合
            fpn_features.append(upsampled + lateral)
        
        # 反转顺序 (从P2到P5)
        fpn_features = fpn_features[::-1]
        
        # 平滑
        fpn_features = [
            self.smooth_convs[i](feat)
            for i, feat in enumerate(fpn_features)
        ]
        
        return fpn_features


class UNetPlusPlusUltimate(nn.Module):
    """
    U-Net++ 极致优化版
    采用 ResNet-101 + FPN + 注意力 + 边界优化
    
    预期性能:
    - mIoU: 75-80% (理论上限)
    - Car IoU: 70-75%
    - Truck IoU: 60-68%
    - Bus IoU: 88-92%
    """
    
    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 4,
        deep_supervision: bool = True,
        pretrained: bool = True,
        use_boundary_refinement: bool = True,
        use_fpn: bool = True,
        attention_type: str = 'cbam_aspp',
        use_separable_conv: bool = True
    ) -> None:
        """
        Args:
            in_channels: 输入通道数
            num_classes: 分割类别数
            deep_supervision: 是否使用深度监督
            pretrained: 是否使用预训练权重
            use_boundary_refinement: 是否使用边界优化
            use_fpn: 是否使用FPN
            attention_type: 注意力类型 ('none', 'cbam', 'se', 'aspp', 'cbam_aspp', 'full')
            use_separable_conv: 是否使用深度可分离卷积
        """
        super(UNetPlusPlusUltimate, self).__init__()
        
        self.deep_supervision = deep_supervision
        self.num_classes = num_classes
        self.use_boundary_refinement = use_boundary_refinement
        self.use_fpn = use_fpn
        self.attention_type = attention_type
        self.use_separable_conv = use_separable_conv
        
        # 加载ResNet-101编码器
        if pretrained:
            resnet = resnet101(weights=ResNet101_Weights.IMAGENET1K_V1)
            print("✓ 加载 ResNet-101 ImageNet预训练权重")
        else:
            resnet = resnet101(weights=None)
            print("✓ 使用 ResNet-101 随机初始化")
        
        # ResNet-101 层提取
        self.conv1 = resnet.conv1    # [B, 64, 256, 256]
        self.bn1 = resnet.bn1
        self.relu = resnet.relu
        self.maxpool = resnet.maxpool  # [B, 64, 128, 128]
        
        self.layer1 = resnet.layer1  # [B, 256, 128, 128]
        self.layer2 = resnet.layer2  # [B, 512, 64, 64]
        self.layer3 = resnet.layer3  # [B, 1024, 32, 32]
        self.layer4 = resnet.layer4  # [B, 2048, 16, 16]
        
        # 编码器输出通道
        encoder_channels = [64, 256, 512, 1024, 2048]
        
        # 解码器通道数
        decoder_channels = [512, 256, 128, 64]
        
        # 设置注意力模块
        self._setup_attention_modules(encoder_channels, attention_type)
        
        # ASPP模块
        self.use_aspp = 'aspp' in attention_type or attention_type == 'full'
        if self.use_aspp:
            self.aspp = ASPP(2048, 512)
            bottleneck_channels = 512  # ASPP输出512通道
        else:
            bottleneck_channels = 2048  # 直接使用ResNet输出
        
        # FPN - 根据是否使用ASPP调整输入通道
        if use_fpn:
            # FPN输入通道: [C2, C3, C4, C5]
            # 如果使用ASPP, C5会变成512通道, 否则是2048通道
            fpn_in_channels = [256, 512, 1024, bottleneck_channels]
            self.fpn = FeaturePyramidNetwork(
                fpn_in_channels,
                out_channels=256
            )
            
            # FPN解码器 (输入为256通道)
            self.decoder4 = self._make_decoder_block(256 + 256, decoder_channels[0])
            self.decoder3 = self._make_decoder_block(decoder_channels[0] + 256, decoder_channels[1])
            self.decoder2 = self._make_decoder_block(decoder_channels[1] + 256, decoder_channels[2])
            self.decoder1 = self._make_decoder_block(decoder_channels[2] + 64, decoder_channels[3])
        else:
            # 原始U-Net解码器
            self.decoder4 = self._make_decoder_block(bottleneck_channels + 1024, decoder_channels[0])
            self.decoder3 = self._make_decoder_block(decoder_channels[0] + 512, decoder_channels[1])
            self.decoder2 = self._make_decoder_block(decoder_channels[1] + 256, decoder_channels[2])
            self.decoder1 = self._make_decoder_block(decoder_channels[2] + 64, decoder_channels[3])
        
        # 边界优化模块
        if use_boundary_refinement:
            self.boundary_refine = BoundaryRefinementModule(decoder_channels[3], num_classes)
        
        # 最终输出
        self.final_conv = nn.Sequential(
            ConvBNReLU(decoder_channels[3], 64, 3, use_separable=use_separable_conv),
            nn.Conv2d(64, num_classes, 1)
        )
        
        # 深度监督输出
        if self.deep_supervision:
            # 根据decoder_channels决定辅助输出的数量
            # FPN模式下只需要decoder4, decoder3, decoder2的输出 (不需要decoder1)
            if use_fpn:
                # FPN模式: 只使用前3个decoder的输出
                aux_decoder_channels = decoder_channels[:3]  # [512, 256, 128]
            else:
                # 非FPN模式: 使用所有decoder的输出
                aux_decoder_channels = decoder_channels  # [512, 256, 128, 64]
            
            self.aux_outputs = nn.ModuleList([
                nn.Conv2d(dec_ch, num_classes, 1)
                for dec_ch in aux_decoder_channels
            ])
            
            # 保存使用的辅助输出数量,用于forward中
            self.num_aux_outputs = len(aux_decoder_channels)
    
    def _make_decoder_block(self, in_channels: int, out_channels: int) -> nn.Module:
        """创建解码器块"""
        return nn.Sequential(
            ConvBNReLU(in_channels, out_channels, 3, use_separable=self.use_separable_conv),
            ConvBNReLU(out_channels, out_channels, 3, use_separable=self.use_separable_conv)
        )
    
    def _setup_attention_modules(self, encoder_channels: List[int], attention_type: str) -> None:
        """设置注意力模块"""
        # 编码器注意力
        if 'cbam' in attention_type or attention_type == 'full':
            self.cbam_layer1 = CBAM(encoder_channels[1])
            self.cbam_layer2 = CBAM(encoder_channels[2])
            self.cbam_layer3 = CBAM(encoder_channels[3])
            self.cbam_layer4 = CBAM(encoder_channels[4])
        
        if 'se' in attention_type or attention_type == 'full':
            self.se_layer1 = SEBlock(encoder_channels[1])
            self.se_layer2 = SEBlock(encoder_channels[2])
            self.se_layer3 = SEBlock(encoder_channels[3])
            self.se_layer4 = SEBlock(encoder_channels[4])
    
    def _apply_encoder_attention(self, x: torch.Tensor, layer_idx: int) -> torch.Tensor:
        """应用编码器注意力"""
        if 'cbam' in self.attention_type or self.attention_type == 'full':
            cbam_modules = [None, self.cbam_layer1, self.cbam_layer2, self.cbam_layer3, self.cbam_layer4]
            if cbam_modules[layer_idx]:
                x = cbam_modules[layer_idx](x)
        
        if 'se' in self.attention_type or self.attention_type == 'full':
            se_modules = [None, self.se_layer1, self.se_layer2, self.se_layer3, self.se_layer4]
            if se_modules[layer_idx]:
                x = se_modules[layer_idx](x)
        
        return x
    
    def forward(self, x: torch.Tensor) -> Union[torch.Tensor, tuple]:
        """前向传播"""
        input_size = x.shape[-2:]
        
        # 编码器路径
        # C1: [B, 64, 256, 256]
        c1 = self.relu(self.bn1(self.conv1(x)))
        c1 = self.maxpool(c1)  # [B, 64, 128, 128]
        
        # C2-C5
        c2 = self.layer1(c1)   # [B, 256, 128, 128]
        c2 = self._apply_encoder_attention(c2, 1)
        
        c3 = self.layer2(c2)   # [B, 512, 64, 64]
        c3 = self._apply_encoder_attention(c3, 2)
        
        c4 = self.layer3(c3)   # [B, 1024, 32, 32]
        c4 = self._apply_encoder_attention(c4, 3)
        
        c5 = self.layer4(c4)   # [B, 2048, 16, 16]
        c5 = self._apply_encoder_attention(c5, 4)
        
        # ASPP
        if self.use_aspp:
            c5 = self.aspp(c5)  # [B, 512, 16, 16]
        
        # FPN
        if self.use_fpn:
            # FPN特征融合
            fpn_features = self.fpn([c2, c3, c4, c5])
            p2, p3, p4, p5 = fpn_features  # 所有特征都是256通道
            
            # 解码器路径
            d4 = self.decoder4(torch.cat([
                F.interpolate(p5, size=p4.shape[-2:], mode='bilinear', align_corners=True),
                p4
            ], dim=1))
            
            d3 = self.decoder3(torch.cat([
                F.interpolate(d4, size=p3.shape[-2:], mode='bilinear', align_corners=True),
                p3
            ], dim=1))
            
            d2 = self.decoder2(torch.cat([
                F.interpolate(d3, size=p2.shape[-2:], mode='bilinear', align_corners=True),
                p2
            ], dim=1))
            
            d1 = self.decoder1(torch.cat([
                F.interpolate(d2, size=c1.shape[-2:], mode='bilinear', align_corners=True),
                c1
            ], dim=1))
        else:
            # 原始U-Net解码器
            d4 = self.decoder4(torch.cat([
                F.interpolate(c5, size=c4.shape[-2:], mode='bilinear', align_corners=True),
                c4
            ], dim=1))
            
            d3 = self.decoder3(torch.cat([
                F.interpolate(d4, size=c3.shape[-2:], mode='bilinear', align_corners=True),
                c3
            ], dim=1))
            
            d2 = self.decoder2(torch.cat([
                F.interpolate(d3, size=c2.shape[-2:], mode='bilinear', align_corners=True),
                c2
            ], dim=1))
            
            d1 = self.decoder1(torch.cat([
                F.interpolate(d2, size=c1.shape[-2:], mode='bilinear', align_corners=True),
                c1
            ], dim=1))
        
        # 边界优化
        boundary = None
        if self.use_boundary_refinement:
            d1, boundary = self.boundary_refine(d1)
        
        # 最终输出
        main_output = self.final_conv(d1)
        main_output = F.interpolate(main_output, size=input_size, mode='bilinear', align_corners=True)
        
        # 深度监督输出
        if self.deep_supervision:
            aux_outputs = []
            # 只使用指定数量的decoder输出
            # FPN模式: d4, d3, d2 (num_aux_outputs=3)
            # 非FPN模式: d4, d3, d2, d1 (num_aux_outputs=4)
            decoder_outputs = [d4, d3, d2, d1]
            for i in range(self.num_aux_outputs):
                dec_output = decoder_outputs[i]
                aux_out = self.aux_outputs[i](dec_output)
                aux_out = F.interpolate(aux_out, size=input_size, mode='bilinear', align_corners=True)
                aux_outputs.append(aux_out)
            
            if self.use_boundary_refinement:
                return main_output, aux_outputs, boundary
            else:
                return main_output, aux_outputs
        else:
            if self.use_boundary_refinement:
                return main_output, boundary
            else:
                return main_output


def create_ultimate_model(
    num_classes: int = 4,
    pretrained: bool = True,
    use_boundary_refinement: bool = True,
    use_fpn: bool = True,
    attention_type: str = 'cbam_aspp',
    use_separable_conv: bool = True
) -> UNetPlusPlusUltimate:
    """
    创建极致优化模型的工厂函数
    
    Args:
        num_classes: 分割类别数
        pretrained: 是否使用预训练权重
        use_boundary_refinement: 是否使用边界优化
        use_fpn: 是否使用FPN
        attention_type: 注意力类型
        use_separable_conv: 是否使用深度可分离卷积
    
    Returns:
        配置好的模型实例
    """
    return UNetPlusPlusUltimate(
        in_channels=3,
        num_classes=num_classes,
        deep_supervision=True,
        pretrained=pretrained,
        use_boundary_refinement=use_boundary_refinement,
        use_fpn=use_fpn,
        attention_type=attention_type,
        use_separable_conv=use_separable_conv
    )


if __name__ == '__main__':
    # 测试模型
    print("="*80)
    print("U-Net++ 极致优化版 测试")
    print("="*80)
    
    # 不同配置
    configs = [
        {'name': '标准', 'use_fpn': True, 'attention_type': 'cbam_aspp', 'use_boundary_refinement': True},
        {'name': '轻量级', 'use_fpn': False, 'attention_type': 'cbam', 'use_boundary_refinement': False},
        {'name': '完整', 'use_fpn': True, 'attention_type': 'full', 'use_boundary_refinement': True},
    ]
    
    for config in configs:
        print(f"\n配置: {config['name']}")
        print("-" * 80)
        
        model = create_ultimate_model(
            num_classes=4,
            pretrained=False,
            use_fpn=config['use_fpn'],
            attention_type=config['attention_type'],
            use_boundary_refinement=config['use_boundary_refinement']
        )
        
        # 测试前向传播
        x = torch.randn(2, 3, 512, 512)
        outputs = model(x)
        
        if isinstance(outputs, tuple):
            if len(outputs) == 3:
                main_out, aux_outs, boundary = outputs
                print(f"主输出: {main_out.shape}")
                print(f"辅助输出: {[out.shape for out in aux_outs]}")
                print(f"边界输出: {boundary.shape}")
            else:
                main_out, aux_outs = outputs
                print(f"主输出: {main_out.shape}")
                print(f"辅助输出: {[out.shape for out in aux_outs]}")
        else:
            print(f"输出形状: {outputs.shape}")
        
        # 参数量统计
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"\n参数量统计:")
        print(f"  总参数: {total_params:,}")
        print(f"  可训练参数: {trainable_params:,}")
        print(f"  模型大小: {total_params * 4 / 1024 / 1024:.2f} MB")
