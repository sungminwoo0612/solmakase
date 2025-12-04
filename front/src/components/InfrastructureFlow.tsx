import React, { useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Node,
  type Edge,
  type Connection,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface InfrastructureFlowProps {
  architecture?: Record<string, unknown>;
}

export const InfrastructureFlow: React.FC<InfrastructureFlowProps> = ({ architecture }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds: Edge[]) => addEdge(params, eds)),
    [setEdges]
  );

  React.useEffect(() => {
    if (architecture) {
      // 아키텍처 데이터를 노드와 엣지로 변환
      const newNodes: Node[] = [];
      const newEdges: Edge[] = [];

      // 간단한 예시: architecture에서 리소스 추출
      if (architecture.components && Array.isArray(architecture.components)) {
        (architecture.components as Array<Record<string, unknown>>).forEach((component, index) => {
          const nodeId = `node-${index}`;
          newNodes.push({
            id: nodeId,
            type: 'default',
            position: { x: (index % 3) * 250, y: Math.floor(index / 3) * 150 },
            data: {
              label: (component.name as string) || `Component ${index + 1}`,
            },
          });

          // 연결 생성 (예시)
          if (index > 0) {
            newEdges.push({
              id: `edge-${index - 1}-${index}`,
              source: `node-${index - 1}`,
              target: nodeId,
            });
          }
        });
      } else {
        // 기본 노드 생성
        newNodes.push({
          id: 'node-1',
          type: 'default',
          position: { x: 250, y: 100 },
          data: { label: 'Web Server' },
        });
        newNodes.push({
          id: 'node-2',
          type: 'default',
          position: { x: 250, y: 250 },
          data: { label: 'Database' },
        });
        newEdges.push({
          id: 'edge-1-2',
          source: 'node-1',
          target: 'node-2',
        });
      }

      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [architecture, setNodes, setEdges]);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
};

