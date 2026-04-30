#!/usr/bin/env python3
"""
使用draw.io MCP绘制系统架构图
"""
import subprocess
import json
import time
import sys

class DrawIOMCPClient:
    def __init__(self):
        self.process = None
        self.session_id = None
        
    def start(self):
        """启动MCP服务器"""
        self.process = subprocess.Popen(
            ['npx', '@next-ai-drawio/mcp-server@latest'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        print("[INFO] MCP服务器已启动")
        
    def call_tool(self, tool_name, arguments=None):
        """调用MCP工具"""
        if arguments is None:
            arguments = {}
            
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        self.process.stdin.write(json.dumps(request) + '\n')
        self.process.stdin.flush()
        
        # 读取响应
        response_line = self.process.stdout.readline()
        
        # 跳过日志行
        while '[MCP-DrawIO]' in response_line or '[INFO]' in response_line:
            response_line = self.process.stdout.readline()
            
        try:
            return json.loads(response_line)
        except json.JSONDecodeError:
            return None
            
    def start_session(self):
        """启动绘图会话"""
        result = self.call_tool('start_session')
        if result and 'result' in result:
            content = result['result']['content'][0]['text']
            print(content)
            if 'Session ID:' in content:
                self.session_id = content.split('Session ID:')[1].split('\n')[0].strip()
            return True
        return False
        
    def create_diagram(self, xml):
        """创建新图表"""
        result = self.call_tool('create_new_diagram', {'xml': xml})
        if result:
            print("[INFO] 图表创建成功")
            return True
        return False
        
    def export_diagram(self, path, format='drawio'):
        """导出图表"""
        result = self.call_tool('export_diagram', {'path': path, 'format': format})
        if result:
            print(f"[INFO] 图表已导出到: {path}")
            return True
        return False
        
    def close(self):
        """关闭MCP服务器"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("[INFO] MCP服务器已关闭")


def create_architecture_diagram_xml():
    """创建系统架构图的XML"""
    return '''<mxGraphModel dx="1434" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1200" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    
    <!-- 标题 -->
    <mxCell id="title" value="道路车辆分割系统 - 系统架构图" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=24;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="500" y="20" width="600" height="40" as="geometry" />
    </mxCell>
    
    <!-- 用户层 -->
    <mxCell id="user-layer" value="用户层" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=16;fontColor=#666666;" vertex="1" parent="1">
      <mxGeometry x="60" y="80" width="100" height="30" as="geometry" />
    </mxCell>
    
    <!-- Web用户 -->
    <mxCell id="web-user" value="Web用户" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="90" width="40" height="80" as="geometry" />
    </mxCell>
    
    <!-- 算法工程师 -->
    <mxCell id="engineer" value="算法工程师" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="500" y="90" width="40" height="80" as="geometry" />
    </mxCell>
    
    <!-- 系统管理员 -->
    <mxCell id="admin" value="系统管理员" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="800" y="90" width="40" height="80" as="geometry" />
    </mxCell>
    
    <!-- 前端层 -->
    <mxCell id="frontend-layer" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="120" y="200" width="1000" height="120" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-title" value="前端层 (Vue 3 + Vite + Element Plus)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#d6b656;" vertex="1" parent="1">
      <mxGeometry x="420" y="210" width="400" height="20" as="geometry" />
    </mxCell>
    
    <!-- 前端组件 -->
    <mxCell id="segment-view" value="图像分割&#xa;Segment.vue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="140" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="history-view" value="历史记录&#xa;History.vue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="260" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="compare-view" value="结果对比&#xa;Compare.vue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="380" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="models-view" value="模型管理&#xa;Models.vue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="500" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="augment-view" value="数据增强&#xa;Augmentation.vue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="620" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="login-view" value="用户登录&#xa;Login.vue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="740" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="router" value="Vue Router" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="880" y="240" width="100" height="60" as="geometry" />
    </mxCell>
    
    <!-- API层 -->
    <mxCell id="api-layer" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="120" y="360" width="1000" height="120" as="geometry" />
    </mxCell>
    
    <mxCell id="api-title" value="API层 (Flask + Flask-RESTful)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="420" y="370" width="400" height="20" as="geometry" />
    </mxCell>
    
    <!-- API路由 -->
    <mxCell id="segment-api" value="/api/segment&#xa;图像分割" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="140" y="400" width="90" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="models-api" value="/api/models&#xa;模型管理" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="250" y="400" width="90" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="augment-api" value="/api/augmentation&#xa;数据增强" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="360" y="400" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="gpu-api" value="/api/gpu/status&#xa;GPU监控" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="480" y="400" width="100" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="auth-api" value="/api/login&#xa;用户认证" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="600" y="400" width="90" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="history-api" value="/api/segment/history&#xa;历史记录" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="710" y="400" width="110" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="compare-api" value="/api/segment/compare&#xa;结果对比" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="840" y="400" width="110" height="60" as="geometry" />
    </mxCell>
    
    <!-- 服务层 -->
    <mxCell id="service-layer" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="120" y="520" width="1000" height="120" as="geometry" />
    </mxCell>
    
    <mxCell id="service-title" value="服务层 (Business Logic)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="420" y="530" width="400" height="20" as="geometry" />
    </mxCell>
    
    <!-- 服务组件 -->
    <mxCell id="model-service" value="模型服务&#xa;ModelService" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="140" y="560" width="120" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="segment-service" value="分割服务&#xa;SegmentService" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="280" y="560" width="120" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="augment-service" value="增强服务&#xa;AugmentationService" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="420" y="560" width="140" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="storage-service" value="存储服务&#xa;StorageService" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="580" y="560" width="120" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="auth-service" value="认证服务&#xa;AuthService" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="720" y="560" width="120" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="gpu-service" value="GPU服务&#xa;GPUService" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="860" y="560" width="120" height="60" as="geometry" />
    </mxCell>
    
    <!-- 核心层 -->
    <mxCell id="core-layer" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="120" y="680" width="1000" height="140" as="geometry" />
    </mxCell>
    
    <mxCell id="core-title" value="核心层 (Deep Learning Models)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#9673a6;" vertex="1" parent="1">
      <mxGeometry x="420" y="690" width="400" height="20" as="geometry" />
    </mxCell>
    
    <!-- 核心组件 -->
    <mxCell id="unet-model" value="U-Net++&#xa;unet_plusplus.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="140" y="720" width="130" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="unet-enhanced" value="U-Net++ Enhanced&#xa;unet_plusplus_enhanced.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="290" y="720" width="150" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="attention" value="注意力模块&#xa;attention_modules.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="460" y="720" width="130" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="losses" value="损失函数&#xa;losses.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="610" y="720" width="110" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset" value="数据集&#xa;dataset.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="740" y="720" width="110" height="60" as="geometry" />
    </mxCell>
    
    <mxCell id="augment-core" value="数据增强&#xa;augmentation.py" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="870" y="720" width="110" height="60" as="geometry" />
    </mxCell>
    
    <!-- 数据层 -->
    <mxCell id="data-layer" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="120" y="860" width="1000" height="100" as="geometry" />
    </mxCell>
    
    <mxCell id="data-title" value="数据层 (Storage & Database)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#b85450;" vertex="1" parent="1">
      <mxGeometry x="420" y="870" width="400" height="20" as="geometry" />
    </mxCell>
    
    <!-- 数据组件 -->
    <mxCell id="file-storage" value="文件存储&#xa;outputs/" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="160" y="900" width="100" height="50" as="geometry" />
    </mxCell>
    
    <mxCell id="database" value="SQLite数据库&#xa;models.db" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="300" y="900" width="110" height="50" as="geometry" />
    </mxCell>
    
    <mxCell id="checkpoints" value="模型检查点&#xa;checkpoints/" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="440" y="900" width="110" height="50" as="geometry" />
    </mxCell>
    
    <mxCell id="uploads" value="上传文件&#xa;uploads/" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="580" y="900" width="100" height="50" as="geometry" />
    </mxCell>
    
    <mxCell id="results" value="分割结果&#xa;results/" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="710" y="900" width="100" height="50" as="geometry" />
    </mxCell>
    
    <mxCell id="logs" value="日志文件&#xa;logs/" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="840" y="900" width="100" height="50" as="geometry" />
    </mxCell>
    
    <!-- 外部工具 -->
    <mxCell id="external-layer" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="120" y="1000" width="1000" height="80" as="geometry" />
    </mxCell>
    
    <mxCell id="external-title" value="外部工具 & 环境" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#666666;" vertex="1" parent="1">
      <mxGeometry x="420" y="1010" width="400" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="pytorch" value="PyTorch" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="160" y="1035" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="cuda" value="CUDA/MPS" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="290" y="1035" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="tensorboard" value="TensorBoard" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="420" y="1035" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="albumentations" value="Albumentations" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="550" y="1035" width="110" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="numpy" value="NumPy" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="690" y="1035" width="80" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="pillow" value="Pillow" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="800" y="1035" width="80" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="opencv" value="OpenCV" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="910" y="1035" width="80" height="35" as="geometry" />
    </mxCell>
    
    <!-- 连接线 - 用户到前端 -->
    <mxCell id="conn-user-frontend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;endArrow=classic;" edge="1" parent="1" source="web-user" target="segment-view">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="conn-eng-frontend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;endArrow=classic;" edge="1" parent="1" source="engineer" target="models-view">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="conn-admin-frontend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;endArrow=classic;" edge="1" parent="1" source="admin" target="models-view">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 连接线 - 前端到API -->
    <mxCell id="conn-frontend-api" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;endArrow=classic;dashed=1;" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="620" y="320" as="sourcePoint" />
        <mxPoint x="620" y="360" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    
    <mxCell id="conn-label-1" value="HTTP/REST API" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontStyle=1;" vertex="1" connectable="0" parent="1" source="conn-frontend-api">
      <mxGeometry x="-0.2" relative="1" as="geometry">
        <mxPoint x="10" y="-9" as="offset" />
      </mxGeometry>
    </mxCell>
    
    <!-- 连接线 - API到服务 -->
    <mxCell id="conn-api-service" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;endArrow=classic;dashed=1;" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="620" y="480" as="sourcePoint" />
        <mxPoint x="620" y="520" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    
    <mxCell id="conn-label-2" value="Service Calls" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontStyle=1;" vertex="1" connectable="0" parent="1" source="conn-api-service">
      <mxGeometry x="-0.2" relative="1" as="geometry">
        <mxPoint x="10" y="-9" as="offset" />
      </mxGeometry>
    </mxCell>
    
    <!-- 连接线 - 服务到核心 -->
    <mxCell id="conn-service-core" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#9673a6;endArrow=classic;dashed=1;" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="620" y="640" as="sourcePoint" />
        <mxPoint x="620" y="680" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    
    <mxCell id="conn-label-3" value="Model Inference" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontStyle=1;" vertex="1" connectable="0" parent="1" source="conn-service-core">
      <mxGeometry x="-0.2" relative="1" as="geometry">
        <mxPoint x="10" y="-9" as="offset" />
      </mxGeometry>
    </mxCell>
    
    <!-- 连接线 - 核心到数据 -->
    <mxCell id="conn-core-data" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#b85450;endArrow=classic;dashed=1;" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="620" y="820" as="sourcePoint" />
        <mxPoint x="620" y="860" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    
    <mxCell id="conn-label-4" value="Read/Write" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontStyle=1;" vertex="1" connectable="0" parent="1" source="conn-core-data">
      <mxGeometry x="-0.2" relative="1" as="geometry">
        <mxPoint x="10" y="-9" as="offset" />
      </mxGeometry>
    </mxCell>
    
    <!-- 图例 -->
    <mxCell id="legend-box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="1180" y="200" width="200" height="280" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-title" value="架构层次" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="1230" y="210" width="100" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-frontend" value="前端层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1200" y="240" width="80" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-api" value="API层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1200" y="280" width="80" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-service" value="服务层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1200" y="320" width="80" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-core" value="核心层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1200" y="360" width="80" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-data" value="数据层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1200" y="400" width="80" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-external" value="外部工具" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1200" y="440" width="80" height="30" as="geometry" />
    </mxCell>
    
  </root>
</mxGraphModel>'''


def main():
    print("=" * 60)
    print("道路车辆分割系统 - 系统架构图绘制")
    print("=" * 60)
    
    client = DrawIOMCPClient()
    
    try:
        # 启动MCP服务器
        print("\n[1/3] 启动draw.io MCP服务器...")
        client.start()
        time.sleep(2)
        
        # 启动会话
        print("\n[2/3] 启动绘图会话...")
        if client.start_session():
            print("✓ 会话启动成功，浏览器窗口已打开")
            time.sleep(3)
            
            # 创建架构图
            print("\n[3/3] 创建系统架构图...")
            xml = create_architecture_diagram_xml()
            if client.create_diagram(xml):
                print("✓ 系统架构图创建成功")
                print("\n请在浏览器中查看实时预览")
                print("架构图包含:")
                print("  - 用户层（Web用户、算法工程师、系统管理员）")
                print("  - 前端层（Vue 3 + Vite + Element Plus）")
                print("  - API层（Flask + Flask-RESTful）")
                print("  - 服务层（业务逻辑）")
                print("  - 核心层（深度学习模型）")
                print("  - 数据层（存储和数据库）")
                print("  - 外部工具（PyTorch、CUDA等）")
                
                # 等待图表渲染
                print("\n等待图表渲染...")
                time.sleep(3)
                
                # 导出图表
                export_path = "/Users/sux/IdeaProjects/maesx.github.io/docs/architecture_diagram.drawio"
                if client.export_diagram(export_path):
                    print(f"\n✓ 图表已导出到: {export_path}")
                else:
                    print("\n✗ 导出图表失败")
            else:
                print("✗ 创建图表失败")
        else:
            print("✗ 启动会话失败")
            
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
    finally:
        client.close()
        print("\n完成！")


if __name__ == '__main__':
    main()