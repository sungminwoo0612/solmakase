import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { infrastructureService } from '../services/infrastructureService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Loading } from '../components/common/Loading';
import { formatters } from '../utils/formatters';
import type { DesignType } from '../types/infrastructure';

export const Infrastructure: React.FC = () => {
  const { requirementId, infrastructureId } = useParams<{ requirementId?: string; infrastructureId?: string }>();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [modifyPrompt, setModifyPrompt] = useState('');

  const { data: infrastructures, isLoading } = useQuery({
    queryKey: ['infrastructures', requirementId],
    queryFn: () => infrastructureService.getRequirementInfrastructures(requirementId!),
    enabled: !!requirementId,
  });

  const { data: comparison } = useQuery({
    queryKey: ['infrastructure-comparison', requirementId],
    queryFn: () => infrastructureService.compareInfrastructures(requirementId!),
    enabled: !!requirementId && !!infrastructures && infrastructures.length > 0,
  });

  const { data: iacCode, isLoading: iacLoading, refetch: refetchIac } = useQuery({
    queryKey: ['iac-code', infrastructureId],
    queryFn: () => infrastructureService.getIaCCode(infrastructureId!),
    enabled: !!infrastructureId,
  });

  const generateIaCMutation = useMutation({
    mutationFn: () => infrastructureService.generateIaCCode(infrastructureId!, 'terraform'),
    onSuccess: () => {
      refetchIac();
    },
    onError: (err: Error) => {
      setError(err.message || 'IaC 코드 생성에 실패했습니다.');
    },
  });

  const modifyIaCMutation = useMutation({
    mutationFn: (prompt: string) => infrastructureService.modifyIaCCode(infrastructureId!, { prompt }),
    onSuccess: () => {
      setModifyPrompt('');
      refetchIac();
    },
    onError: (err: Error) => {
      setError(err.message || '코드 수정에 실패했습니다.');
    },
  });

  const createDesignMutation = useMutation({
    mutationFn: ({ designType, provider }: { designType: DesignType; provider?: string }) =>
      infrastructureService.createDesign(requirementId!, designType, provider),
    onSuccess: (data) => {
      navigate(`/infrastructure/${data.id}/iac`);
    },
    onError: (err: Error) => {
      setError(err.message || '설계 생성에 실패했습니다.');
    },
  });

  const handleCreateDesign = (designType: DesignType) => {
    setError(null);
    createDesignMutation.mutate({ designType });
  };

  const handleSelectDesign = (id: string) => {
     navigate(`/infrastructure/${id}/iac`);
  };

  if (isLoading) {
    return <Loading text="인프라 설계안을 불러오는 중..." />;
  }

  // IaC 코드 페이지 (infrastructureId가 있고 requirementId가 없는 경우)
  if (infrastructureId && !requirementId) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">IaC 코드</h1>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>오류</AlertTitle>
            <AlertDescription>
              {error}
              <Button
                variant="ghost"
                size="sm"
                className="ml-2"
                onClick={() => setError(null)}
              >
                닫기
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {!iacCode && !iacLoading && (
          <Card>
            <CardHeader>
              <CardTitle>코드 생성</CardTitle>
              <CardDescription>
                Terraform 코드를 생성합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => generateIaCMutation.mutate()}
                disabled={generateIaCMutation.isPending}
              >
                {generateIaCMutation.isPending ? '생성 중...' : 'Terraform 코드 생성'}
              </Button>
            </CardContent>
          </Card>
        )}

        {iacLoading && <Loading text="IaC 코드를 불러오는 중..." />}

        {iacCode && (
          <>
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>코드 수정</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">수정 프롬프트</label>
                    <Input
                      value={modifyPrompt}
                      onChange={(e) => setModifyPrompt(e.target.value)}
                      placeholder="예: CPU를 4코어로 변경해주세요"
                    />
                  </div>
                  <Button
                    onClick={() => modifyIaCMutation.mutate(modifyPrompt)}
                    disabled={modifyIaCMutation.isPending || !modifyPrompt.trim()}
                  >
                    {modifyIaCMutation.isPending ? '수정 중...' : '코드 수정'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Terraform 코드 (버전 {iacCode.version})</CardTitle>
                    <CardDescription>상태: {iacCode.status}</CardDescription>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate(`/downloads/${infrastructureId}`)}
                  >
                    다운로드
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm max-h-96">
                  {iacCode.code}
                </pre>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">인프라 설계</h1>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>오류</AlertTitle>
          <AlertDescription>
            {error}
            <Button
              variant="ghost"
              size="sm"
              className="ml-2"
              onClick={() => setError(null)}
            >
              닫기
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {(!infrastructures || infrastructures.length === 0) && (
        <Card>
          <CardHeader>
            <CardTitle>설계안 생성</CardTitle>
            <CardDescription>
              온프레미스 또는 클라우드 인프라 설계안을 생성합니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4">
              <Button
                onClick={() => handleCreateDesign('onprem')}
                disabled={createDesignMutation.isPending}
              >
                {createDesignMutation.isPending ? '생성 중...' : '온프레미스 설계안 생성'}
              </Button>
              <Button
                onClick={() => handleCreateDesign('cloud')}
                disabled={createDesignMutation.isPending}
              >
                {createDesignMutation.isPending ? '생성 중...' : '클라우드 설계안 생성'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {infrastructures && infrastructures.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {infrastructures.map((infra) => (
              <Card key={infra.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>
                        {infra.design_type === 'onprem' ? '온프레미스' : '클라우드'} 설계안
                      </CardTitle>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleSelectDesign(infra.id)}
                    >
                      선택
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm text-muted-foreground">상태</p>
                      <p className="font-medium">{infra.status}</p>
                    </div>
                    {infra.cost_estimate && (
                      <div>
                        <p className="text-sm text-muted-foreground">예상 비용</p>
                        <p className="font-medium">
                          {infra.cost_estimate.monthly
                            ? formatters.formatCurrency(infra.cost_estimate.monthly as number)
                            : '-'}
                        </p>
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-muted-foreground">생성일</p>
                      <p className="font-medium">{formatters.formatDate(infra.created_at)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {comparison && (comparison.onprem || comparison.cloud) && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>비용 비교</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {comparison.onprem && comparison.onprem.cost_estimate && (
                    <div>
                      <p className="text-sm text-muted-foreground">온프레미스</p>
                      <p className="text-2xl font-bold">
                        {formatters.formatCurrency(
                          (comparison.onprem.cost_estimate.monthly as number) || 0
                        )}
                      </p>
                    </div>
                  )}
                  {comparison.cloud && comparison.cloud.cost_estimate && (
                    <div>
                      <p className="text-sm text-muted-foreground">클라우드</p>
                      <p className="text-2xl font-bold">
                        {formatters.formatCurrency(
                          (comparison.cloud.cost_estimate.monthly as number) || 0
                        )}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

