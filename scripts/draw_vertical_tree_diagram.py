#!/usr/bin/env python3
"""
使用draw.io MCP绘制纵向树状代码结构图
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


def create_vertical_tree_xml():
    """创建纵向树状代码结构图的XML"""
    return '''<mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="2000" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    
    <!-- 标题 -->
    <mxCell id="title" value="道路车辆分割系统 - 代码结构树" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=24;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="350" y="20" width="500" height="40" as="geometry" />
    </mxCell>
    
    <!-- 根节点 -->
    <mxCell id="root" value="📁 maesx.github.io/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=18;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="450" y="80" width="300" height="50" as="geometry" />
    </mxCell>
    
    <!-- 第一层：主要目录 -->
    <mxCell id="src" value="📁 src/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="100" y="180" width="200" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="configs" value="📁 configs/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="350" y="180" width="200" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="scripts" value="📁 scripts/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="600" y="180" width="200" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="tests" value="📁 tests/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="850" y="180" width="200" height="45" as="geometry" />
    </mxCell>
    
    <!-- 第二层：src子目录 -->
    <mxCell id="src-models" value="📁 models/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="40" y="280" width="140" height="40" as="geometry" />
    </mxCell>
    
    <mxCell id="src-data" value="📁 data/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="40" y="340" width="140" height="40" as="geometry" />
    </mxCell>
    
    <mxCell id="src-training" value="📁 training/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="40" y="400" width="140" height="40" as="geometry" />
    </mxCell>
    
    <mxCell id="src-inference" value="📁 inference/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="40" y="460" width="140" height="40" as="geometry" />
    </mxCell>
    
    <mxCell id="src-utils" value="📁 utils/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="40" y="520" width="140" height="40" as="geometry" />
    </mxCell>
    
    <mxCell id="src-web" value="📁 web/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;" vertex="1" parent="1">
      <mxGeometry x="40" y="580" width="140" height="40" as="geometry" />
    </mxCell>
    
    <!-- 第三层：models文件 -->
    <mxCell id="models-files" value="📄 unet_plusplus.py&#xa;📄 attention_modules.py&#xa;📄 unet_plusplus_enhanced.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="200" y="280" width="180" height="55" as="geometry" />
    </mxCell>
    
    <!-- 第三层：data文件 -->
    <mxCell id="data-files" value="📄 dataset.py&#xa;📄 yolo_to_mask.py&#xa;📄 augmentation_optimized.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="200" y="340" width="180" height="55" as="geometry" />
    </mxCell>
    
    <!-- 第三层：training文件 -->
    <mxCell id="training-files" value="📄 train.py&#xa;📄 train_optimized.py&#xa;📄 train_ultimate.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="200" y="400" width="180" height="55" as="geometry" />
    </mxCell>
    
    <!-- 第三层：inference文件 -->
    <mxCell id="inference-files" value="📄 inference.py&#xa;📄 inference_enhanced.py&#xa;📄 inference_instance.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="200" y="460" width="180" height="55" as="geometry" />
    </mxCell>
    
    <!-- 第三层：utils文件 -->
    <mxCell id="utils-files" value="📄 losses.py&#xa;📄 exceptions.py&#xa;📄 logging_config.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="200" y="520" width="180" height="55" as="geometry" />
    </mxCell>
    
    <!-- web子目录 -->
    <mxCell id="web-backend" value="📁 backend/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;" vertex="1" parent="1">
      <mxGeometry x="200" y="580" width="120" height="35" as="geometry" />
    </mxCell>
    
    <mxCell id="web-frontend" value="📁 frontend/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="1">
      <mxGeometry x="340" y="580" width="120" height="35" as="geometry" />
    </mxCell>
    
    <!-- backend子目录 -->
    <mxCell id="backend-routes" value="📁 routes/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="200" y="630" width="90" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="backend-services" value="📁 services/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="300" y="630" width="90" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="backend-db" value="📁 database/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="400" y="630" width="90" height="30" as="geometry" />
    </mxCell>
    
    <!-- frontend子目录 -->
    <mxCell id="frontend-views" value="📁 views/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="200" y="670" width="90" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-components" value="📁 components/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="300" y="670" width="100" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="frontend-api" value="📁 api/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="410" y="670" width="80" height="30" as="geometry" />
    </mxCell>
    
    <!-- configs文件 -->
    <mxCell id="config-file" value="📄 config.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="240" width="120" height="30" as="geometry" />
    </mxCell>
    
    <!-- scripts文件 -->
    <mxCell id="scripts-files" value="📄 quick_train.sh&#xa;📄 init_database.py&#xa;📄 evaluate.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="600" y="240" width="140" height="55" as="geometry" />
    </mxCell>
    
    <!-- tests文件 -->
    <mxCell id="tests-files" value="📄 test_model.py&#xa;📄 test_system.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#9673a6;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="850" y="240" width="140" height="45" as="geometry" />
    </mxCell>
    
    <!-- docs文件 -->
    <mxCell id="docs" value="📁 docs/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="100" y="750" width="200" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="docs-files" value="📄 README.md&#xa;📄 INFERENCE_GUIDE.md&#xa;📄 TRAINING_GUIDE.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="350" y="750" width="160" height="55" as="geometry" />
    </mxCell>
    
    <!-- outputs目录 -->
    <mxCell id="outputs" value="📁 outputs/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="100" y="830" width="200" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="outputs-checkpoints" value="📁 checkpoints/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="830" width="110" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="outputs-logs" value="📁 logs/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="470" y="830" width="90" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="outputs-results" value="📁 results/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="570" y="830" width="90" height="30" as="geometry" />
    </mxCell>
    
    <!-- 数据集目录 -->
    <mxCell id="dataset" value="📁 road_vehicle_pedestrian_det_datasets/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="100" y="910" width="300" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-images" value="📁 images/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="450" y="910" width="90" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-labels" value="📁 labels/" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="550" y="910" width="90" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="dataset-classes" value="📄 classes.txt" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d79b00;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="650" y="910" width="100" height="30" as="geometry" />
    </mxCell>
    
    <!-- 根目录文件 -->
    <mxCell id="root-files" value="📄 根目录文件" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=16;" vertex="1" parent="1">
      <mxGeometry x="100" y="990" width="200" height="45" as="geometry" />
    </mxCell>
    
    <mxCell id="root-files-list" value="📄 train.py&#xa;📄 inference.py&#xa;📄 start_server.py&#xa;📄 requirements.txt&#xa;📄 README.md" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;spacingTop=5;" vertex="1" parent="1">
      <mxGeometry x="350" y="990" width="140" height="85" as="geometry" />
    </mxCell>
    
    <!-- 连接线 - 根节点到第一层 -->
    <mxCell id="edge-root-src" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="root" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-configs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d6b656;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="root" target="configs">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-scripts" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#82b366;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="root" target="scripts">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-tests" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#9673a6;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="root" target="tests">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- src到子目录 -->
    <mxCell id="edge-src-models" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#9673a6;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="src-models" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-data" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#82b366;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="src-data" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-training" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#d6b656;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="src-training" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-inference" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#b85450;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="src-inference" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-utils" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#d79b00;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="src-utils" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-src-web" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#6c8ebf;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="src-web" target="src">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 子目录到文件 -->
    <mxCell id="edge-models-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#9673a6;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-models" target="models-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-data-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#82b366;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-data" target="data-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-training-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-training" target="training-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-inference-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#b85450;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-inference" target="inference-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-utils-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-utils" target="utils-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- web到子目录 -->
    <mxCell id="edge-web-backend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-web" target="web-backend">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-web-frontend" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="src-web" target="web-frontend">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- backend到子目录 -->
    <mxCell id="edge-backend-routes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="web-backend" target="backend-routes">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-backend-services" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="web-backend" target="backend-services">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-backend-db" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="web-backend" target="backend-db">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- frontend到子目录 -->
    <mxCell id="edge-frontend-views" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="web-frontend" target="frontend-views">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-frontend-components" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="web-frontend" target="frontend-components">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-frontend-api" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#6c8ebf;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="web-frontend" target="frontend-api">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 其他连接 -->
    <mxCell id="edge-configs-file" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d6b656;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="configs" target="config-file">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-scripts-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#82b366;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="scripts" target="scripts-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-tests-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#9673a6;endArrow=none;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="tests" target="tests-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-docs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="docs" target="root">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-docs-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="docs" target="docs-files">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-outputs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#b85450;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="outputs" target="root">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-outputs-checkpoints" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#b85450;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="outputs" target="outputs-checkpoints">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-outputs-logs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#b85450;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="outputs" target="outputs-logs">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-outputs-results" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#b85450;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="outputs" target="outputs-results">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-dataset" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d79b00;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="dataset" target="root">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-dataset-images" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="dataset" target="dataset-images">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-dataset-labels" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="dataset" target="dataset-labels">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-dataset-classes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#d79b00;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="dataset" target="dataset-classes">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#666666;endArrow=none;exitX=0;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1" source="root-files" target="root">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <mxCell id="edge-root-files-list" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;endArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="root-files" target="root-files-list">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    
    <!-- 图例 -->
    <mxCell id="legend-box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;strokeWidth=2;" vertex="1" parent="1">
      <mxGeometry x="750" y="320" width="380" height="280" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-title" value="目录说明" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1;fontSize=16;fontColor=#333333;" vertex="1" parent="1">
      <mxGeometry x="880" y="330" width="120" height="25" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-src" value="📁 src/ - 源代码" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="770" y="365" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-configs" value="📁 configs/ - 配置" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="950" y="365" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-scripts" value="📁 scripts/ - 脚本" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="770" y="405" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-tests" value="📁 tests/ - 测试" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="950" y="405" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-docs" value="📁 docs/ - 文档" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="770" y="445" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-outputs" value="📁 outputs/ - 输出" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="950" y="445" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-models" value="📁 models/ - 模型" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="770" y="485" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-training" value="📁 training/ - 训练" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="950" y="485" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-inference" value="📁 inference/ - 推理" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="770" y="525" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-data" value="📁 data/ - 数据" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="950" y="525" width="160" height="30" as="geometry" />
    </mxCell>
    
    <mxCell id="legend-utils" value="📁 utils/ - 工具" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;align=left;spacingLeft=10;" vertex="1" parent="1">
      <mxGeometry x="860" y="565" width="160" height="30" as="geometry" />
    </mxCell>
    
  </root>
</mxGraphModel>'''


def main():
    print("=" * 60)
    print("道路车辆分割系统 - 纵向树状代码结构图绘制")
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
            
            # 创建纵向树状结构图
            print("\n[3/3] 创建纵向树状代码结构图...")
            xml = create_vertical_tree_xml()
            if client.create_diagram(xml):
                print("✓ 纵向树状代码结构图创建成功")
                print("\n请在浏览器中查看实时预览")
                print("纵向树状结构图特点:")
                print("  - 从上到下的树状结构")
                print("  - 清晰的层级关系")
                print("  - 颜色编码区分不同模块")
                print("  - 适合纵向阅读和打印")
                
                # 等待图表渲染
                print("\n等待图表渲染...")
                time.sleep(3)
                
                # 导出图表
                export_path = "/Users/sux/IdeaProjects/maesx.github.io/docs/code_tree_vertical.drawio"
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