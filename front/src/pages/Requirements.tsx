import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { requirementService } from '../services/requirementService';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Select } from '../components/common/Select';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { Alert } from '../components/common/Alert';
import type { RequirementCreate, InputType, DeploymentType, Scale } from '../types/requirement';

const TEMP_USER_ID = '00000000-0000-0000-0000-000000000000'; // 임시 사용자 ID

export const Requirements: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'survey' | 'document' | 'chat' | 'expert'>('survey');
  const [formData, setFormData] = useState<Partial<RequirementCreate>>({
    user_id: TEMP_USER_ID,
    input_type: 'survey',
  });
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [requirementId, setRequirementId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: (data: RequirementCreate) => requirementService.createRequirement(data),
    onSuccess: (data) => {
      setRequirementId(data.id);
      navigate(`/analysis/${data.id}`);
    },
    onError: (err: Error) => {
      setError(err.message || '요구사항 생성에 실패했습니다.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const data: RequirementCreate = {
      user_id: TEMP_USER_ID,
      input_type: activeTab as InputType,
      ...formData,
    } as RequirementCreate;
    createMutation.mutate(data);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setUploadedFiles([...uploadedFiles, ...files]);
      // 요구사항 생성 후 파일 업로드
      if (!requirementId) {
        const data: RequirementCreate = {
          user_id: TEMP_USER_ID,
          input_type: 'document',
        };
        try {
          const result = await requirementService.createRequirement(data);
          setRequirementId(result.id);
          // 파일 업로드
          for (const file of files) {
            await requirementService.uploadDocument(result.id, file);
          }
        } catch (err) {
          setError((err as Error).message || '파일 업로드에 실패했습니다.');
        }
      } else {
        for (const file of files) {
          await requirementService.uploadDocument(requirementId, file);
        }
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">요구사항 입력</h1>

      {error && (
        <Alert type="error" message={error} onClose={() => setError(null)} />
      )}

      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {(['survey', 'document', 'chat', 'expert'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab === 'survey' && '설문조사'}
              {tab === 'document' && '문서 업로드'}
              {tab === 'chat' && '채팅 입력'}
              {tab === 'expert' && '전문가 모드'}
            </button>
          ))}
        </nav>
      </div>

      <form onSubmit={handleSubmit}>
        {activeTab === 'survey' && (
          <Card title="설문조사 입력">
            <div className="space-y-4">
              <Input
                label="서비스 종류"
                value={formData.service_type || ''}
                onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
                placeholder="예: 웹 애플리케이션, API 서버 등"
              />
              <Select
                label="배포 유형"
                value={formData.deployment_type || ''}
                onChange={(e) => setFormData({ ...formData, deployment_type: e.target.value as DeploymentType })}
                options={[
                  { value: '', label: '선택하세요' },
                  { value: 'onprem', label: '온프레미스' },
                  { value: 'cloud', label: '클라우드' },
                  { value: 'hybrid', label: '하이브리드' },
                ]}
              />
              <Select
                label="규모"
                value={formData.scale || ''}
                onChange={(e) => setFormData({ ...formData, scale: e.target.value as Scale })}
                options={[
                  { value: '', label: '선택하세요' },
                  { value: 'small', label: '소규모' },
                  { value: 'medium', label: '중규모' },
                  { value: 'large', label: '대규모' },
                ]}
              />
              <Input
                label="예산 (원)"
                type="number"
                value={formData.budget || ''}
                onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
                placeholder="예: 1000000"
              />
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.has_ops_team || false}
                    onChange={(e) => setFormData({ ...formData, has_ops_team: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">운영 인력 보유</span>
                </label>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  특이사항
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  value={formData.special_requirements || ''}
                  onChange={(e) => setFormData({ ...formData, special_requirements: e.target.value })}
                  placeholder="추가 요구사항을 입력하세요"
                />
              </div>
            </div>
          </Card>
        )}

        {activeTab === 'document' && (
          <Card title="문서 업로드">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  파일 선택 (PDF, DOCX, PPTX, 한글)
                </label>
                <input
                  type="file"
                  multiple
                  accept=".pdf,.docx,.pptx,.hwp"
                  onChange={handleFileUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              {uploadedFiles.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">업로드된 파일:</p>
                  <ul className="list-disc list-inside text-sm text-gray-600">
                    {uploadedFiles.map((file, index) => (
                      <li key={index}>{file.name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        )}

        {activeTab === 'chat' && (
          <Card title="채팅 입력">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  요구사항 설명
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={6}
                  value={formData.special_requirements || ''}
                  onChange={(e) => setFormData({ ...formData, special_requirements: e.target.value })}
                  placeholder="인프라 요구사항을 자유롭게 설명해주세요"
                />
              </div>
            </div>
          </Card>
        )}

        {activeTab === 'expert' && (
          <Card title="전문가 모드">
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">필요한 기능 선택:</p>
                <div className="space-y-2">
                  {['로그인 기능', '파일 서버', '객체 스토리지', '데이터베이스', '캐시', '메시지 큐'].map((feature) => (
                    <label key={feature} className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span className="text-sm text-gray-700">{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        )}

        <div className="mt-6 flex justify-end">
          <Button
            type="submit"
            isLoading={createMutation.isPending}
            disabled={createMutation.isPending}
          >
            {activeTab === 'document' ? '파일 업로드 완료' : '요구사항 제출'}
          </Button>
        </div>
      </form>
    </div>
  );
};

