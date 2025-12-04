import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { infrastructureService } from '../services/infrastructureService';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';

export const Downloads: React.FC = () => {
  const { infrastructureId } = useParams<{ infrastructureId: string }>();

  const { data: iacCode, isLoading } = useQuery({
    queryKey: ['iac-code', infrastructureId],
    queryFn: () => infrastructureService.getIaCCode(infrastructureId!),
    enabled: !!infrastructureId,
  });

  const handleDownloadCode = () => {
    if (iacCode) {
      const blob = new Blob([iacCode.code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `terraform-${iacCode.version}.tf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  if (isLoading) {
    return <Loading text="IaC 코드를 불러오는 중..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">결과물 다운로드</h1>

      {iacCode && (
        <>
          <Card title="IaC 코드 다운로드" className="mb-6">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">도구</p>
                <p className="font-medium">{iacCode.iac_tool}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">버전</p>
                <p className="font-medium">{iacCode.version}</p>
              </div>
              <Button onClick={handleDownloadCode}>
                Terraform 코드 다운로드
              </Button>
            </div>
          </Card>

          <Card title="코드 미리보기">
            <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-sm max-h-96">
              {iacCode.code}
            </pre>
          </Card>
        </>
      )}

      {!iacCode && (
        <Card title="다운로드 가능한 파일이 없습니다">
          <p className="text-gray-600">
            먼저 IaC 코드를 생성해주세요.
          </p>
        </Card>
      )}
    </div>
  );
};

