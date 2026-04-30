#!/usr/bin/env python3
"""
使用draw.io MCP绘制简洁的树状代码结构图
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


def create_tree_structure_xml():
    """创建树状代码结构图的XML - 纵向布局"""
    return '''<mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1600" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    
    <!-- 标题 -->
    <mxCell id="title" value="道路车辆分割系统 - 代码结构树" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=22;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="500" y="20" width="400" height="35" as="geometry" />
    </mxCell>
    
    <!-- 根节点 -->
    <mxCell id="root" value="📁 maesx.github.io/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=16;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="580" y="80" width="240" height="45" as="geometry" />
    </mxCell>
    
    <!-- 第一层：主要目录 - 纵向排列 -->
    <!-- src目录 -->
    <mxCell id="src" value="📁 src/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="200" y="180" width="180" height="40" as="geometry" />
    </mxCell>
    
    <!-- configs目录 -->
    <mxCell id="configs" value="📁 configs/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="420" y="180" width="180" height="40" as="geometry" />
    </mxCell>
    
    <!-- scripts目录 -->
    <mxCell id="scripts" value="📁 scripts/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="640" y="180" width="180" height="40" as="geometry" />
    </mxCell>
    
    <!-- tests目录 -->
    <mxCell id="tests" value="📁 tests/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="860" y="180" width="180" height="40" as="geometry" />
    </mxCell>
    
    <!-- docs目录 -->
    <mxCell id="docs" value="📁 docs/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="1080" y="180" width="180" height="40" as="geometry" />
    </mxCell>
    
    <!-- 第二层：src子目录 -->
    <mxCell id="src-models" value="📁 models/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="40" y="220" width="120" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="src-data" value="📁 data/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="40" y="260" width="120" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="src-training" value="📁 training/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="40" y="300" width="120" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="src-inference" value="📁 inference/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="40" y="340" width="120" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="src-utils" value="📁 utils/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="40" y="380" width="120" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="src-web" value="📁 web/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="40" y="420" width="120" height="30" as="geometry" />
    </mxCell>
    
    <!-- 第三层：models文件 -->
    <mxCell id="models-files" value="unet_plusplus.py&#xa;attention_modules.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="170" y="220" width="130" height="30" as="geometry" />
    </mxCell>
    
    <!-- 第三层：data文件 -->
    <mxCell id="data-files" value="dataset.py&#xa;yolo_to_mask.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="170" y="260" width="130" height="30" as="geometry" />
    </mxCell>
    
    <!-- 第三层：training文件 -->
    <mxCell id="training-files" value="train.py&#xa;train_optimized.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="170" y="300" width="130" height="30" as="geometry" />
    </mxCell>
    
    <!-- 第三层：inference文件 -->
    <mxCell id="inference-files" value="inference.py&#xa;inference_instance.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="170" y="340" width="130" height="30" as="geometry" />
    </mxCell>
    
    <!-- 第三层：utils文件 -->
    <mxCell id="utils-files" value="losses.py&#xa;exceptions.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="170" y="380" width="130" height="30" as="geometry" />
    </mxCell>
    
    <!-- web子目录 -->
    <mxCell id="web-backend" value="📁 backend/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="40" y="460" width="100" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="web-frontend" value="📁 frontend/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="40" y="490" width="100" height="25" as="geometry" />
    </mxCell>
    
    <!-- backend子目录 -->
    <mxCell id="backend-routes" value="routes/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="150" y="460" width="60" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="backend-services" value="services/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="220" y="460" width="60" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="backend-db" value="database/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="290" y="460" width="60" height="25" as="geometry" />
    </mxCell>
    
    <!-- frontend子目录 -->
    <mxCell id="frontend-views" value="views/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="150" y="490" width="60" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-components" value="components/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="220" y="490" width="80" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-api" value="api/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="310" y="490" width="50" height="25" as="geometry" />
    </mxCell>
    
    <!-- configs文件 -->
    <mxCell id="config-file" value="config.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="300" y="195" width="100" height="25" as="geometry" />
    </mxCell>
    
    <!-- scripts文件 -->
    <mxCell id="scripts-files" value="quick_train.sh&#xa;init_database.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="500" y="195" width="120" height="30" as="geometry" />
    </mxCell>
    
    <!-- tests文件 -->
    <mxCell id="tests-files" value="test_model.py&#xa;test_system.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="700" y="195" width="120" height="30" as="geometry" />
    </mxCell>
    
    <!-- docs文件 -->
    <mxCell id="docs-files" value="README.md&#xa;INFERENCE_GUIDE.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="900" y="195" width="130" height="30" as="geometry" />
    </mxCell>
    
    <!-- outputs子目录 -->
    <mxCell id="outputs-checkpoints" value="checkpoints/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="1100" y="195" width="80" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="outputs-logs" value="logs/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="1190" y="195" width="50" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="outputs-results" value="results/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="1250" y="195" width="60" height="25" as="geometry" />
    </mxCell>
    
    <!-- 根目录文件列表 -->
    <mxCell id="root-files-list" value="train.py&#xa;inference.py&#xa;start_server.py&#xa;requirements.txt" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=10;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="1280" y="195" width="100" height="50" as="geometry" />
    </mxCell>
    
    <!-- 数据集目录 -->
    <mxCell id="dataset" value="📁 road_vehicle_pedestrian_det_datasets/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="700" y="260" width="260" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-images" value="images/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="700" y="305" width="70" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-labels" value="labels/" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="780" y="305" width="70" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-classes" value="classes.txt" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=10;" vertex="1" parent="1">
      <mxGeometry x="860" y="305" width="80" height="25" as="geometry" />
    </mxCell>
    
    <!-- 连接线 -->
    <!-- 根节点到第一层 -->
    <mxCell id="edge-root-src" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;endArrow=none;" edge="1" parent="1" source="root" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-configs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="root" target="configs">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-scripts" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;endArrow=none;" edge="1" parent="1" source="root" target="scripts">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-tests" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#9673a6;endArrow=none;" edge="1" parent="1" source="root" target="tests">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-docs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="root" target="docs">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-outputs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#b85450;endArrow=none;" edge="1" parent="1" source="root" target="outputs">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#666666;endArrow=none;" edge="1" parent="1" source="root" target="root-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- src到子目录 -->
    <mxCell id="edge-src-models" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#9673a6;endArrow=none;" edge="1" parent="1" source="src" target="src-models">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-data" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#82b366;endArrow=none;" edge="1" parent="1" source="src" target="src-data">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-training" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="src" target="src-training">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-inference" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#b85450;endArrow=none;" edge="1" parent="1" source="src" target="src-inference">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-utils" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="src" target="src-utils">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-web" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#6c8ebf;endArrow=none;" edge="1" parent="1" source="src" target="src-web">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- web到子目录 -->
    <mxCell id="edge-web-backend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="src-web" target="web-backend">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-web-frontend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;" edge="1" parent="1" source="src-web" target="web-frontend">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- backend到子目录 -->
    <mxCell id="edge-backend-routes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="web-backend" target="backend-routes">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-backend-services" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="web-backend" target="backend-services">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-backend-db" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="web-backend" target="backend-db">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- frontend到子目录 -->
    <mxCell id="edge-frontend-views" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;" edge="1" parent="1" source="web-frontend" target="frontend-views">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-frontend-components" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;" edge="1" parent="1" source="web-frontend" target="frontend-components">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-frontend-api" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;" edge="1" parent="1" source="web-frontend" target="frontend-api">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 子目录到文件 -->
    <mxCell id="edge-models-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#9673a6;endArrow=none;" edge="1" parent="1" source="src-models" target="models-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-data-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#82b366;endArrow=none;" edge="1" parent="1" source="src-data" target="data-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-training-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;" edge="1" parent="1" source="src-training" target="training-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-inference-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#b85450;endArrow=none;" edge="1" parent="1" source="src-inference" target="inference-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-utils-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="src-utils" target="utils-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 数据集连接 -->
    <mxCell id="edge-root-dataset" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="root" target="dataset">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-dataset-images" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="dataset" target="dataset-images">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-dataset-labels" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="dataset" target="dataset-labels">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-dataset-classes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;" edge="1" parent="1" source="dataset" target="dataset-classes">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 图例 -->
    <mxCell id="legend-box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="40" y="550" width="400" height="180" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-title" value="目录说明" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=14;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="180" y="560" width="120" height="20" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-src" value="src/ - 源代码" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="60" y="590" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-configs" value="configs/ - 配置" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="180" y="590" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-scripts" value="scripts/ - 脚本" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="300" y="590" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-tests" value="tests/ - 测试" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="60" y="625" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-docs" value="docs/ - 文档" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="180" y="625" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-outputs" value="outputs/ - 输出" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="300" y="625" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-models" value="models/ - 模型" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="60" y="660" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-training" value="training/ - 训练" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="180" y="660" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-inference" value="inference/ - 推理" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="300" y="660" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-data" value="data/ - 数据" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="60" y="695" width="110" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-utils" value="utils/ - 工具" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;" vertex="1" parent="1">
      <mxGeometry x="180" y="695" width="110" height="25" as="geometry" />
    </mxCell>
    
  </root>
</mxGraphModel>'''


def main():
    print("=" * 60)
    print("道路车辆分割系统 - 简洁树状代码结构图绘制")
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
            
            # 创建树状结构图
            print("\n[3/3] 创建简洁树状代码结构图...")
            xml = create_tree_structure_xml()
            if client.create_diagram(xml):
                print("✓ 树状代码结构图创建成功")
                print("\n请在浏览器中查看实时预览")
                print("树状结构图包含:")
                print("  - 根目录 (maesx.github.io/)")
                print("  - 主要目录 (src/, configs/, scripts/, tests/, docs/, outputs/)")
                print("  - src子目录 (models/, data/, training/, inference/, utils/, web/)")
                print("  - web子目录 (backend/, frontend/)")
                print("  - 数据集目录")
                print("  - 根目录文件")
                
                # 等待图表渲染
                print("\n等待图表渲染...")
                time.sleep(3)
                
                # 导出图表
                export_path = "/Users/sux/IdeaProjects/maesx.github.io/docs/code_tree_diagram.drawio"
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