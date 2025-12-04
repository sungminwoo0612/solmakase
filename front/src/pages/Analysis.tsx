import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { analysisService } from '../services/analysisService';
import { requirementService } from '../services/requirementService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Loading } from '../components/common/Loading';
import { formatters } from '../utils/formatters';

// 분석 데이터를 구조화된 형태로 표시하는 컴포넌트
const AnalysisDataView: React.FC<{ data: Record<string, unknown> }> = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return <p className="text-muted-foreground">분석 데이터가 없습니다.</p>;
  }

  const renderValue = (value: unknown): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="text-muted-foreground">-</span>;
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="text-muted-foreground">없음</span>;
      }
      return (
        <ul className="list-disc list-inside space-y-1">
          {value.map((item: unknown, index: number) => (
            <li key={index}>{String(item)}</li>
          ))}
        </ul>
      );
    }
    
    if (typeof value === 'object') {
      return (
        <pre className="bg-muted p-2 rounded text-xs overflow-auto">
          {JSON.stringify(value, null, 2)}
        </pre>
      );
    }
    
    return <span>{String(value)}</span>;
  };

  const getLabel = (key: string): string => {
    const labels: Record<string, string> = {
      service_type: '서비스 종류',
      deployment_type: '배포 유형',
      scale: '규모',
      required_features: '필요한 기능',
      estimated_users: '예상 사용자 수',
      performance_requirements: '성능 요구사항',
      security_requirements: '보안 요구사항',
      budget_range: '예산 범위',
      technical_stack_suggestions: '기술 스택 제안',
      raw_response: '원본 응답',
      error: '에러',
    };
    return labels[key] || key;
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(data).map(([key, value]) => {
          // 에러나 원본 응답은 별도로 표시
          if (key === 'error' || key === 'raw_response') {
            return null;
          }
          
          return (
            <div key={key} className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">{getLabel(key)}</p>
              <div className="text-base">{renderValue(value)}</div>
            </div>
          );
        })}
      </div>
      
      {/* 에러나 원본 응답이 있으면 표시 */}
      {((data.error !== undefined && data.error !== null) || 
        (data.raw_response !== undefined && data.raw_response !== null)) && (
        <div className="mt-4 space-y-2">
          {data.error !== undefined && data.error !== null && (
            <Alert variant="destructive">
              <AlertTitle>에러</AlertTitle>
              <AlertDescription>{String(data.error)}</AlertDescription>
            </Alert>
          )}
          {data.raw_response !== undefined && data.raw_response !== null && (
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">원본 응답</p>
              <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                {String(data.raw_response)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const Analysis: React.FC = () => {
  const { requirementId } = useParams<{ requirementId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [pollingStartTime, setPollingStartTime] = useState<number | null>(null);

  // 최대 폴링 시간: 5분 (300초)
  const MAX_POLLING_TIME_MS = 5 * 60 * 1000;

  const { data: requirement, isLoading: requirementLoading } = useQuery({
    queryKey: ['requirement', requirementId],
    queryFn: () => requirementService.getRequirement(requirementId!),
    enabled: !!requirementId,
  });

  const { data: analysis, isLoading: analysisLoading, refetch } = useQuery({
    queryKey: ['analysis', requirementId],
    queryFn: () => analysisService.getAnalysisResult(requirementId!),
    enabled: !!requirementId,
    refetchInterval: (query) => {
      const data = query.state.data;
      
      // 실패 상태면 폴링 중단
      if (data?.status === 'failed') {
        setPollingStartTime(null);
        return false;
      }
      
      // 분석 중이거나 대기 중일 때만 폴링 (더 빠른 업데이트)
      if (data?.status === 'pending' || data?.status === 'analyzing') {
        // 폴링 시작 시간 기록
        if (!pollingStartTime) {
          setPollingStartTime(Date.now());
        }
        
        // 최대 시간 초과 시 폴링 중단
        if (pollingStartTime && Date.now() - pollingStartTime > MAX_POLLING_TIME_MS) {
          setError('분석 시간이 너무 오래 걸립니다. 잠시 후 다시 시도해주세요.');
          setPollingStartTime(null);
          return false;
        }
        
        return 1000; // 1초마다 폴링 (실시간 업데이트)
      }
      
      // 완료되면 폴링 중단
      if (data?.status === 'completed') {
        setPollingStartTime(null);
      }
      
      return false;
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: () => analysisService.analyzeRequirement(requirementId!),
    onSuccess: () => {
      setPollingStartTime(Date.now()); // 폴링 시작 시간 기록
      setError(null); // 성공 시 에러 메시지 제거
      queryClient.invalidateQueries({ queryKey: ['analysis', requirementId] });
    },
    onError: (err: any) => {
      const errorMessage = err?.response?.data?.detail || err?.message || '분석 실행에 실패했습니다.';
      setError(errorMessage);
      setPollingStartTime(null);
      
      // LLM API 키 관련 에러인 경우 더 명확한 메시지
      if (errorMessage.includes('OPENAI_API_KEY') || errorMessage.includes('LLM 서비스')) {
        setError('LLM 서비스가 설정되지 않았습니다. OPENAI_API_KEY를 설정해주세요.');
      }
    },
  });

  const handleAnalyze = () => {
    setError(null);
    setPollingStartTime(null);
    analyzeMutation.mutate();
  };

  const handleNext = () => {
    if (requirementId) {
      navigate(`/design/${requirementId}`);
    }
  };

  // 요구사항이 pending 상태이고 분석이 시작되지 않았으면 자동으로 분석 시작
  useEffect(() => {
    if (
      requirement &&
      requirement.status === 'pending' &&
      !analysis &&
      !analysisLoading &&
      !analyzeMutation.isPending &&
      !error
    ) {
      // 약간의 지연 후 자동 시작 (사용자가 화면을 볼 시간 제공)
      const timer = setTimeout(() => {
        handleAnalyze();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [requirement, analysis, analysisLoading, analyzeMutation.isPending, error]);

  if (requirementLoading) {
    return <Loading text="요구사항 정보를 불러오는 중..." />;
  }

  const isAnalyzing = analysis?.status === 'pending' || analysis?.status === 'analyzing';
  const isCompleted = analysis?.status === 'completed';

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">분석 결과</h1>

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

      {requirement && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>요구사항 요약</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">서비스 종류</p>
                <p className="font-medium">{requirement.service_type || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">배포 유형</p>
                <p className="font-medium">{requirement.deployment_type || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">규모</p>
                <p className="font-medium">{requirement.scale || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">예산</p>
                <p className="font-medium">
                  {requirement.budget ? formatters.formatCurrency(requirement.budget) : '-'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {!analysis && !analysisLoading && (
        <Card>
          <CardHeader>
            <CardTitle>분석 실행</CardTitle>
            <CardDescription>
              요구사항을 분석하여 구조화된 데이터를 생성합니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleAnalyze} disabled={analyzeMutation.isPending}>
              {analyzeMutation.isPending ? '분석 중...' : '분석 시작'}
            </Button>
          </CardContent>
        </Card>
      )}

      {analysisLoading && (
        <Loading text="분석 결과를 불러오는 중..." />
      )}

      {isAnalyzing && (
        <>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>분석 진행 중</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <Loading size="sm" text="" />
                <div className="ml-4 flex-1">
                  <p className="text-muted-foreground">요구사항을 분석하고 있습니다. 잠시만 기다려주세요...</p>
                  {pollingStartTime && (
                    <>
                      <p className="text-xs text-muted-foreground mt-1">
                        경과 시간: {Math.floor((Date.now() - pollingStartTime) / 1000)}초
                      </p>
                      {Date.now() - pollingStartTime > 30000 && (
                        <p className="text-xs text-amber-600 mt-1">
                          ⚠️ 분석이 예상보다 오래 걸리고 있습니다. LLM API 키가 올바르게 설정되었는지 확인해주세요.
                        </p>
                      )}
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* 분석 중에도 부분 결과가 있으면 표시 */}
          {analysis?.analysis_data && Object.keys(analysis.analysis_data).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>분석 중인 데이터 (실시간 업데이트)</CardTitle>
                <CardDescription>분석이 완료되기 전에도 확인할 수 있는 부분 결과입니다.</CardDescription>
              </CardHeader>
              <CardContent>
                <AnalysisDataView data={analysis.analysis_data} />
              </CardContent>
            </Card>
          )}
        </>
      )}

      {isCompleted && analysis && (
        <>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>분석 완료</CardTitle>
              <CardDescription>요구사항 분석이 완료되었습니다.</CardDescription>
            </CardHeader>
            <CardContent>
              <AnalysisDataView data={analysis.analysis_data} />
            </CardContent>
          </Card>

          <div className="flex justify-end space-x-4">
            <Button variant="outline" onClick={() => refetch()}>
              새로고침
            </Button>
            <Button onClick={handleNext}>
              다음 단계: 인프라 설계
            </Button>
          </div>
        </>
      )}

      {analysis?.status === 'failed' && (
        <Card>
          <CardHeader>
            <CardTitle>분석 실패</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>오류</AlertTitle>
              <AlertDescription>
                분석 중 오류가 발생했습니다.
                <br />
                <br />
                가능한 원인:
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>LLM API 키(OPENAI_API_KEY)가 설정되지 않았습니다.</li>
                  <li>LLM API 호출에 실패했습니다.</li>
                  <li>분석 시간이 초과되었습니다.</li>
                </ul>
                <br />
                <strong>해결 방법:</strong> backend/.env 파일에 OPENAI_API_KEY를 설정하고 서버를 재시작해주세요.
              </AlertDescription>
            </Alert>
            <div className="flex gap-2">
              <Button onClick={handleAnalyze}>다시 시도</Button>
              <Button variant="outline" onClick={() => refetch()}>
                상태 새로고침
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

