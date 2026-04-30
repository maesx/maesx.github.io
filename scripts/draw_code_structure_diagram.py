#!/usr/bin/env python3
"""
使用draw.io MCP绘制代码结构图
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


def create_code_structure_diagram_xml():
    """创建代码结构图的XML"""
    return '''<mxGraphModel dx="1434" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1800" pageHeight="1400" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    
    <!-- 标题 -->
    <mxCell id="title" value="道路车辆分割系统 - 代码结构图" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=24;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="600" y="20" width="600" height="40" as="geometry" />
    </mxCell>
    
    <!-- 项目根目录 -->
    <mxCell id="root-package" value="maesx.github.io/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="60" y="80" width="1680" height="1280" as="geometry" />
    </mxCell>
    
    <!-- src目录 -->
    <mxCell id="src-package" value="src/" style="swimlane;horizontal=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=13;startSize=30;" vertex="1" parent="1">
      <mxGeometry x="80" y="120" width="800" height="1220" as="geometry" />
    </mxCell>
    
    <!-- models模块 -->
    <mxCell id="models-package" value="models/" style="swimlane;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="100" y="160" width="360" height="220" as="geometry" />
    </mxCell>
    
    <mxCell id="models-init" value="__init__.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="120" y="195" width="150" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="unet-pp" value="unet_plusplus.py&#xa;U-Net++ 模型" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="230" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="unet-pp-enhanced" value="unet_plusplus_enhanced.py&#xa;增强版 U-Net++" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="275" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="unet-pp-ultimate" value="unet_plusplus_ultimate.py&#xa;终极版 U-Net++" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="320" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="attention" value="attention_modules.py&#xa;注意力模块" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="230" width="150" height="35" as="geometry" />
    </mxCell>
    
    <!-- data模块 -->
    <mxCell id="data-package" value="data/" style="swimlane;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="100" y="400" width="360" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="data-init" value="__init__.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="120" y="435" width="150" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset" value="dataset.py&#xa;数据集加载" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="470" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="yolo-convert" value="yolo_to_mask.py&#xa;YOLO标注转换" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="435" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="augment" value="augmentation_optimized.py&#xa;数据增强" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="480" width="150" height="35" as="geometry" />
    </mxCell>
    
    <!-- training模块 -->
    <mxCell id="training-package" value="training/" style="swimlane;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="100" y="600" width="360" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="training-init" value="__init__.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="120" y="635" width="150" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="train-py" value="train.py&#xa;训练脚本" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="670" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="train-opt" value="train_optimized.py&#xa;优化训练" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="635" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="train-ult" value="train_ultimate.py&#xa;终极训练" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="680" width="150" height="35" as="geometry" />
    </mxCell>
    
    <!-- inference模块 -->
    <mxCell id="inference-package" value="inference/" style="swimlane;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="100" y="800" width="360" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="inference-init" value="__init__.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="120" y="835" width="150" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="inference-py" value="inference.py&#xa;推理脚本" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="870" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="inference-enh" value="inference_enhanced.py&#xa;增强推理" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="835" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="inference-inst" value="inference_instance.py&#xa;实例分割" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="880" width="150" height="35" as="geometry" />
    </mxCell>
    
    <!-- utils模块 -->
    <mxCell id="utils-package" value="utils/" style="swimlane;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="100" y="1000" width="360" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="utils-init" value="__init__.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="120" y="1035" width="150" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="losses" value="losses.py&#xa;损失函数" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="120" y="1070" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="exceptions" value="exceptions.py&#xa;异常定义" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="1035" width="150" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="logging" value="logging_config.py&#xa;日志配置" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="290" y="1080" width="150" height="35" as="geometry" />
    </mxCell>
    
    <!-- web模块 -->
    <mxCell id="web-package" value="web/" style="swimlane;horizontal=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=13;startSize=30;" vertex="1" parent="1">
      <mxGeometry x="480" y="160" width="380" height="1180" as="geometry" />
    </mxCell>
    
    <!-- backend模块 -->
    <mxCell id="backend-package" value="backend/" style="swimlane;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="500" y="200" width="340" height="540" as="geometry" />
    </mxCell>
    
    <mxCell id="app-py" value="app.py&#xa;Flask应用入口" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="520" y="235" width="140" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="app-config" value="app_config.py&#xa;应用配置" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="680" y="235" width="140" height="35" as="geometry" />
    </mxCell>
    
    <!-- routes子模块 -->
    <mxCell id="routes-package" value="routes/" style="swimlane;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="520" y="280" width="300" height="140" as="geometry" />
    </mxCell>
    
    <mxCell id="route-segment" value="segment.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="530" y="310" width="90" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="route-models" value="models.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="630" y="310" width="90" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="route-augment" value="augmentation.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="730" y="310" width="80" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="route-auth" value="auth.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="530" y="345" width="90" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="route-viz" value="visualization.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="630" y="345" width="90" height="25" as="geometry" />
    </mxCell>
    
    <!-- services子模块 -->
    <mxCell id="services-package" value="services/" style="swimlane;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="520" y="430" width="300" height="100" as="geometry" />
    </mxCell>
    
    <mxCell id="service-model" value="model_service.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="530" y="460" width="90" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="service-storage" value="storage_service.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="630" y="460" width="90" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="service-augment" value="augmentation_service.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="730" y="460" width="80" height="25" as="geometry" />
    </mxCell>
    
    <!-- database子模块 -->
    <mxCell id="database-package" value="database/" style="swimlane;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="520" y="540" width="300" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="db-session" value="session.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="530" y="570" width="90" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="db-models" value="models/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=9;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="630" y="570" width="170" height="130" as="geometry" />
    </mxCell>
    
    <mxCell id="db-model-user" value="user.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=8;" vertex="1" parent="1">
      <mxGeometry x="640" y="595" width="70" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="db-model-dataset" value="dataset.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=8;" vertex="1" parent="1">
      <mxGeometry x="720" y="595" width="70" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="db-model-model" value="model.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=8;" vertex="1" parent="1">
      <mxGeometry x="640" y="620" width="70" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="db-model-seg" value="segmentation.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=8;" vertex="1" parent="1">
      <mxGeometry x="720" y="620" width="70" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="db-model-aug" value="augmentation.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=8;" vertex="1" parent="1">
      <mxGeometry x="640" y="645" width="70" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="db-model-log" value="log.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=8;" vertex="1" parent="1">
      <mxGeometry x="720" y="645" width="70" height="20" as="geometry" />
    </mxCell>
    
    <!-- frontend模块 -->
    <mxCell id="frontend-package" value="frontend/" style="swimlane;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="500" y="760" width="340" height="560" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-src" value="src/" style="swimlane;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="520" y="795" width="300" height="500" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-main" value="main.js&#xa;入口文件" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="540" y="825" width="90" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-app" value="App.vue&#xa;根组件" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="640" y="825" width="90" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-router" value="router/&#xa;index.js" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="740" y="825" width="60" height="35" as="geometry" />
    </mxCell>
    
    <!-- views子模块 -->
    <mxCell id="views-package" value="views/" style="swimlane;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="540" y="870" width="260" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="view-segment" value="Segment.vue&#xa;图像分割" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="550" y="900" width="80" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="view-history" value="History.vue&#xa;历史记录" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="640" y="900" width="80" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="view-compare" value="Compare.vue&#xa;结果对比" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="730" y="900" width="60" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="view-models" value="Models.vue&#xa;模型管理" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="550" y="945" width="80" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="view-augment" value="Augmentation.vue&#xa;数据增强" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="640" y="945" width="80" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="view-login" value="Login.vue&#xa;用户登录" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="730" y="945" width="60" height="35" as="geometry" />
    </mxCell>
    
    <!-- components子模块 -->
    <mxCell id="components-package" value="components/" style="swimlane;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="540" y="1060" width="260" height="100" as="geometry" />
    </mxCell>
    
    <mxCell id="comp-image-compare" value="ImageCompare.vue&#xa;图像对比组件" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="550" y="1090" width="120" height="35" as="geometry" />
    </mxCell>
    
    <!-- api子模块 -->
    <mxCell id="api-package" value="api/" style="swimlane;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=11;startSize=20;" vertex="1" parent="1">
      <mxGeometry x="540" y="1170" width="260" height="100" as="geometry" />
    </mxCell>
    
    <mxCell id="api-index" value="index.js&#xa;API封装" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="550" y="1200" width="120" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="api-modules" value="modules.js&#xa;模型API" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=9;align=center;" vertex="1" parent="1">
      <mxGeometry x="680" y="1200" width="110" height="35" as="geometry" />
    </mxCell>
    
    <!-- 其他目录 -->
    <mxCell id="other-package" value="其他目录" style="swimlane;horizontal=0;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=13;startSize=30;" vertex="1" parent="1">
      <mxGeometry x="900" y="120" width="820" height="1220" as="geometry" />
    </mxCell>
    
    <!-- configs目录 -->
    <mxCell id="configs-package" value="configs/" style="swimlane;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="920" y="160" width="360" height="100" as="geometry" />
    </mxCell>
    
    <mxCell id="config-py" value="config.py&#xa;配置文件" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="195" width="150" height="35" as="geometry" />
    </mxCell>
    
    <!-- scripts目录 -->
    <mxCell id="scripts-package" value="scripts/" style="swimlane;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="920" y="280" width="360" height="140" as="geometry" />
    </mxCell>
    
    <mxCell id="script-train" value="quick_train.sh&#xa;快速训练" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="315" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="script-train-infer" value="train_and_infer.sh&#xa;训练推理" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1050" y="315" width="110" height="35" as="geometry" />
    </mxCell>
    
    <!-- tests目录 -->
    <mxCell id="tests-package" value="tests/" style="swimlane;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="920" y="440" width="360" height="140" as="geometry" />
    </mxCell>
    
    <mxCell id="test-model" value="test_model.py&#xa;模型测试" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="475" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="test-system" value="test_system.py&#xa;系统测试" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1050" y="475" width="110" height="35" as="geometry" />
    </mxCell>
    
    <!-- docs目录 -->
    <mxCell id="docs-package" value="docs/" style="swimlane;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="920" y="600" width="360" height="220" as="geometry" />
    </mxCell>
    
    <mxCell id="doc-readme" value="README.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="940" y="635" width="80" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="doc-inference" value="INFERENCE_GUIDE.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="1030" y="635" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="doc-instance" value="INSTANCE_SEGMENTATION_GUIDE.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="1150" y="635" width="120" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="doc-color" value="COLOR_SCHEME_GUIDE.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="940" y="670" width="120" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="doc-training" value="OPTIMIZED_TRAINING_GUIDE.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=9;" vertex="1" parent="1">
      <mxGeometry x="1070" y="670" width="140" height="25" as="geometry" />
    </mxCell>
    
    <!-- outputs目录 -->
    <mxCell id="outputs-package" value="outputs/" style="swimlane;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="920" y="840" width="360" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="output-checkpoints" value="checkpoints/&#xa;模型检查点" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="875" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="output-logs" value="logs/&#xa;训练日志" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1050" y="875" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="output-results" value="results/&#xa;分割结果" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1160" y="875" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="output-uploads" value="uploads/&#xa;上传文件" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="920" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="output-masks" value="masks/&#xa;分割掩码" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1050" y="920" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="output-viz" value="visualizations/&#xa;可视化结果" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1160" y="920" width="100" height="35" as="geometry" />
    </mxCell>
    
    <!-- 根目录文件 -->
    <mxCell id="root-files" value="根目录文件" style="swimlane;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="920" y="1040" width="360" height="280" as="geometry" />
    </mxCell>
    
    <mxCell id="root-train" value="train.py&#xa;训练入口" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="1075" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="root-inference" value="inference.py&#xa;推理入口" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1050" y="1075" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="root-start" value="start_server.py&#xa;启动脚本" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1160" y="1075" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="root-requirements" value="requirements.txt&#xa;Python依赖" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="940" y="1120" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="root-readme" value="README.md&#xa;项目文档" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1050" y="1120" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="root-gitignore" value=".gitignore&#xa;Git配置" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1160" y="1120" width="100" height="35" as="geometry" />
    </mxCell>
    
    <!-- 数据集目录 -->
    <mxCell id="dataset-package" value="road_vehicle_pedestrian_det_datasets/" style="swimlane;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=12;startSize=25;" vertex="1" parent="1">
      <mxGeometry x="1320" y="160" width="380" height="140" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-images" value="images/&#xa;图像数据" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1340" y="195" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-labels" value="labels/&#xa;标注文件" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1450" y="195" width="100" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-classes" value="classes.txt&#xa;类别定义" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=center;" vertex="1" parent="1">
      <mxGeometry x="1560" y="195" width="120" height="35" as="geometry" />
    </mxCell>
    
    <!-- 图例 -->
    <mxCell id="legend-box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="1320" y="320" width="380" height="280" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-title" value="模块说明" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="1450" y="330" width="120" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-models" value="models/ - 模型架构" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1340" y="360" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-data" value="data/ - 数据处理" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1520" y="360" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-training" value="training/ - 训练模块" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1340" y="400" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-inference" value="inference/ - 推理模块" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1520" y="400" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-utils" value="utils/ - 工具函数" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1340" y="440" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-web" value="web/ - Web平台" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1520" y="440" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-backend" value="backend/ - 后端API" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1340" y="480" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-frontend" value="frontend/ - 前端界面" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1520" y="480" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-database" value="database/ - 数据库" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1340" y="520" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-outputs" value="outputs/ - 输出目录" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="1520" y="520" width="160" height="30" as="geometry" />
    </mxCell>
    
  </root>
</mxGraphModel>'''


def main():
    print("=" * 60)
    print("道路车辆分割系统 - 代码结构图绘制")
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
            
            # 创建代码结构图
            print("\n[3/3] 创建代码结构图...")
            xml = create_code_structure_diagram_xml()
            if client.create_diagram(xml):
                print("✓ 代码结构图创建成功")
                print("\n请在浏览器中查看实时预览")
                print("代码结构图包含:")
                print("  - src/ 源代码目录")
                print("    - models/ - 模型架构")
                print("    - data/ - 数据处理")
                print("    - training/ - 训练模块")
                print("    - inference/ - 推理模块")
                print("    - utils/ - 工具函数")
                print("    - web/ - Web平台")
                print("  - configs/ - 配置文件")
                print("  - scripts/ - 脚本工具")
                print("  - tests/ - 测试文件")
                print("  - docs/ - 文档目录")
                print("  - outputs/ - 输出目录")
                print("  - 数据集目录")
                print("  - 根目录文件")
                
                # 等待图表渲染
                print("\n等待图表渲染...")
                time.sleep(3)
                
                # 导出图表
                export_path = "/Users/sux/IdeaProjects/maesx.github.io/docs/code_structure_diagram.drawio"
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