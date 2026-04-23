"""
注意力机制模块
包含 CBAM, SE-Net, ASPP 等注意力模块实现
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ChannelAttention(nn.Module):
    """
    通道注意力模块 (Channel Attention Module)
    关注"什么特征重要" - 自适应调整通道权重
    """
    def __init__(self, in_channels: int, ratio: int = 16) -> None:
        """
        Args:
            in_channels: 输入通道数
            ratio: 降维比例,用于减少参数量
        """
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        
        # 共享MLP
        self.fc = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // ratio, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // ratio, in_channels, 1, bias=False)
        )
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 并行计算平均池化和最大池化分支
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        # 融合两个分支
        out = self.sigmoid(avg_out + max_out)
        return x * out


class SpatialAttention(nn.Module):
    """
    空间注意力模块 (Spatial Attention Module)
    关注"哪里重要" - 突出关键空间位置
    """
    def __init__(self, kernel_size: int = 7) -> None:
        """
        Args:
            kernel_size: 卷积核大小,通常为7或3
        """
        super(SpatialAttention, self).__init__()
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 沿通道维度计算平均和最大值
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        # 拼接并生成空间注意力图
        out = torch.cat([avg_out, max_out], dim=1)
        out = self.sigmoid(self.conv(out))
        return x * out


class CBAM(nn.Module):
    """
    Convolutional Block Attention Module
    通道注意力 + 空间注意力的级联组合
    论文: CBAM: Convolutional Block Attention Module (ECCV 2018)
    """
    def __init__(self, in_channels: int, ratio: int = 16, kernel_size: int = 7) -> None:
        """
        Args:
            in_channels: 输入通道数
            ratio: 通道注意力的降维比例
            kernel_size: 空间注意力的卷积核大小
        """
        super(CBAM, self).__init__()
        self.channel_attention = ChannelAttention(in_channels, ratio)
        self.spatial_attention = SpatialAttention(kernel_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 先通道注意力,后空间注意力
        x = self.channel_attention(x)
        x = self.spatial_attention(x)
        return x


class SEBlock(nn.Module):
    """
    Squeeze-and-Excitation Block
    轻量级通道注意力
    论文: Squeeze-and-Excitation Networks (CVPR 2018)
    """
    def __init__(self, in_channels: int, ratio: int = 16) -> None:
        """
        Args:
            in_channels: 输入通道数
            ratio: 降维比例
        """
        super(SEBlock, self).__init__()
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Linear(in_channels, in_channels // ratio, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(in_channels // ratio, in_channels, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, _, _ = x.size()
        # Squeeze: 全局平均池化
        y = self.squeeze(x).view(b, c)
        # Excitation: 学习通道权重
        y = self.excitation(y).view(b, c, 1, 1)
        # Scale: 重新校准特征
        return x * y.expand_as(x)


class ASPPConv(nn.Module):
    """ASPP中的空洞卷积分支"""
    def __init__(self, in_channels: int, out_channels: int, dilation: int) -> None:
        super(ASPPConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=dilation, dilation=dilation, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class ASPPPooling(nn.Module):
    """ASPP中的全局平均池化分支"""
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super(ASPPPooling, self).__init__()
        self.conv = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        size = x.shape[-2:]
        x = self.conv(x)
        return F.interpolate(x, size=size, mode='bilinear', align_corners=True)


class ASPP(nn.Module):
    """
    Atrous Spatial Pyramid Pooling
    多尺度特征提取模块,捕获不同尺度的上下文信息
    论文: DeepLab v3+ (ECCV 2018)
    """
    def __init__(self, in_channels: int, out_channels: int = 256, dilations: tuple = (6, 12, 18)) -> None:
        """
        Args:
            in_channels: 输入通道数
            out_channels: 输出通道数
            dilations: 空洞卷积的膨胀率列表
        """
        super(ASPP, self).__init__()
        
        modules = []
        
        # 1x1卷积分支
        modules.append(nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        ))
        
        # 不同膨胀率的空洞卷积分支
        for dilation in dilations:
            modules.append(ASPPConv(in_channels, out_channels, dilation))
        
        # 全局平均池化分支
        modules.append(ASPPPooling(in_channels, out_channels))
        
        self.convs = nn.ModuleList(modules)
        
        # 融合层
        self.project = nn.Sequential(
            nn.Conv2d(out_channels * (len(dilations) + 2), out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = []
        for conv in self.convs:
            res.append(conv(x))
        res = torch.cat(res, dim=1)
        return self.project(res)


class DualAttention(nn.Module):
    """
    双注意力模块: 位置注意力 + 通道注意力
    论文: Dual Attention Network for Scene Segmentation (CVPR 2019)
    """
    def __init__(self, in_channels: int) -> None:
        super(DualAttention, self).__init__()
        # 位置注意力
        self.query_conv = nn.Conv2d(in_channels, in_channels // 8, 1)
        self.key_conv = nn.Conv2d(in_channels, in_channels // 8, 1)
        self.value_conv = nn.Conv2d(in_channels, in_channels, 1)
        self.gamma = nn.Parameter(torch.zeros(1))
        
        # 通道注意力
        self.channel_gamma = nn.Parameter(torch.zeros(1))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, C, H, W = x.size()
        
        # 位置注意力
        query = self.query_conv(x).view(batch_size, -1, H * W).permute(0, 2, 1)
        key = self.key_conv(x).view(batch_size, -1, H * W)
        energy = torch.bmm(query, key)
        attention = F.softmax(energy, dim=-1)
        value = self.value_conv(x).view(batch_size, -1, H * W)
        position_out = torch.bmm(value, attention.permute(0, 2, 1)).view(batch_size, C, H, W)
        position_out = self.gamma * position_out + x
        
        # 通道注意力
        channel_query = position_out.view(batch_size, C, -1)
        channel_key = position_out.view(batch_size, C, -1).permute(0, 2, 1)
        channel_energy = torch.bmm(channel_query, channel_key)
        channel_attention = F.softmax(channel_energy, dim=-1)
        channel_value = position_out.view(batch_size, C, -1)
        channel_out = torch.bmm(channel_attention, channel_value).view(batch_size, C, H, W)
        channel_out = self.channel_gamma * channel_out + position_out
        
        return channel_out


if __name__ == '__main__':
    # 测试各个注意力模块
    print("测试注意力模块...")
    
    x = torch.randn(2, 256, 64, 64)
    
    # 测试CBAM
    cbam = CBAM(256)
    out_cbam = cbam(x)
    print(f"CBAM - 输入: {x.shape}, 输出: {out_cbam.shape}")
    
    # 测试SE
    se = SEBlock(256)
    out_se = se(x)
    print(f"SE Block - 输入: {x.shape}, 输出: {out_se.shape}")
    
    # 测试ASPP
    aspp = ASPP(256, 256)
    out_aspp = aspp(x)
    print(f"ASPP - 输入: {x.shape}, 输出: {out_aspp.shape}")
    
    # 测试Dual Attention
    da = DualAttention(256)
    out_da = da(x)
    print(f"Dual Attention - 输入: {x.shape}, 输出: {out_da.shape}")
    
    # 计算参数量
    print(f"\n参数量统计:")
    print(f"CBAM: {sum(p.numel() for p in cbam.parameters()):,}")
    print(f"SE Block: {sum(p.numel() for p in se.parameters()):,}")
    print(f"ASPP: {sum(p.numel() for p in aspp.parameters()):,}")
    print(f"Dual Attention: {sum(p.numel() for p in da.parameters()):,}")
