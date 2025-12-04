import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { requirementService } from '../services/requirementService';
import type { RequirementCreate } from '../types/requirement';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const demoMutation = useMutation({
    mutationFn: async () => {
      const payload: RequirementCreate = {
        user_id: '00000000-0000-0000-0000-000000000000',
        input_type: 'survey',
        service_type: '샘플 웹 서비스',
        deployment_type: 'onprem',
        scale: 'small',
        budget: 0,
        has_ops_team: false,
        special_requirements: '데모용 온프레미스 인프라 설계 시나리오',
      };
      const created = await requirementService.createRequirement(payload);
      return created;
    },
    onSuccess: (created) => {
      navigate(`/analysis/${created.id}`);
    },
  });

  const features = [
    {
      title: '요구사항 수집',
      description: '설문조사, 문서 업로드, 채팅 등 다양한 방식으로 인프라 요구사항을 수집합니다.',
      icon: '📝',
    },
    {
      title: 'AI 기반 분석',
      description: 'RAG와 Agent LLM을 활용하여 요구사항을 분석하고 구조화합니다.',
      icon: '🤖',
    },
    {
      title: '인프라 설계',
      description: '온프레미스와 클라우드 설계안을 자동 생성하고 비용을 비교합니다.',
      icon: '🏗️',
    },
    {
      title: 'IaC 코드 생성',
      description: 'Terraform 코드를 자동 생성하고 프롬프트로 수정할 수 있습니다.',
      icon: '💻',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Solmakase
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          AI 기반 인프라 설계 및 IaC 코드 자동 생성 플랫폼
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            size="lg"
            onClick={() => navigate('/requirements')}
          >
            요구사항 입력 시작하기
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => demoMutation.mutate()}
            disabled={demoMutation.isPending}
          >
            {demoMutation.isPending ? '데모 시나리오 준비 중...' : '예시 시나리오 바로 실행'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        {features.map((feature, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{feature.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-start">
                <span className="text-4xl mr-4">{feature.icon}</span>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>주요 기능</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-muted-foreground">
            <li>✅ 다중 입력 채널 지원 (설문조사, 문서, 채팅, 전문가 모드)</li>
            <li>✅ RAG 기반 문서 분석 및 요구사항 추출</li>
            <li>✅ 온프레미스/클라우드 인프라 설계안 자동 생성</li>
            <li>✅ 비용 비교 및 견적서 생성</li>
            <li>✅ Terraform IaC 코드 자동 생성</li>
            <li>✅ 프롬프트 기반 코드 수정</li>
            <li>✅ React Flow 기반 인프라 시각화</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

