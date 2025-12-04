import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { infrastructureService } from '../services/infrastructureService';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { InfrastructureFlow } from '../components/InfrastructureFlow';

export const Deployment: React.FC = () => {
  const { infrastructureId } = useParams<{ infrastructureId: string }>();

  const { data: infrastructure, isLoading } = useQuery({
    queryKey: ['infrastructure', infrastructureId],
    queryFn: () => infrastructureService.getInfrastructure(infrastructureId!),
    enabled: !!infrastructureId,
  });

  if (isLoading) {
    return <Loading text="인프라 정보를 불러오는 중..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">배포 및 모니터링</h1>

      {infrastructure && (
        <Card title="인프라 정보">
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">설계 유형</p>
              <p className="font-medium">{infrastructure.design_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">상태</p>
              <p className="font-medium">{infrastructure.status}</p>
            </div>
            {infrastructure.architecture && (
              <div>
                <p className="text-sm text-gray-600 mb-2">아키텍처</p>
                <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-sm">
                  {JSON.stringify(infrastructure.architecture, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </Card>
      )}

      <Card title="인프라 구조 시각화" className="mt-6">
        {infrastructure?.architecture ? (
          <InfrastructureFlow architecture={infrastructure.architecture} />
        ) : (
          <p className="text-gray-600">
            아키텍처 정보가 없습니다.
          </p>
        )}
      </Card>
    </div>
  );
};

