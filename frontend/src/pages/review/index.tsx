import React, { useMemo, useState } from 'react'
import { ReviewQueue } from './components/ReviewQueue'
import { useReviewCounts } from '@/lib/hooks/useReview'
import { Card, CardBody } from '@/components/UI/Card'
import { Spinner } from '@/components/UI/Spinner'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/UI/Tabs'

export default function ReviewPage() {
  const { data: counts, isLoading } = useReviewCounts()
  const [activeTab, setActiveTab] = useState('all')

  const highStakesCount = useMemo(() => {
    if (!counts) return 0
    return (counts.senior || 0) + (counts.follow_up || 0) + (counts.email_reply || 0) + (counts.ambiguous || 0)
  }, [counts])

  const typeLabels: Record<string, string> = {
    standard: 'Standard',
    senior: 'Senior',
    ambiguous: 'Ambiguous',
    resume_failed: 'Resume Failed',
    follow_up: 'Follow-up',
    email_reply: 'Email Reply',
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Review Queue</h1>
      </div>

      {/* Queue Stats */}
      {counts && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(counts).map(([type, count]) => (
            <Card key={type}>
              <CardBody>
                <p className="text-xs text-gray-500 uppercase">{typeLabels[type]}</p>
                <p className="text-2xl font-semibold mt-1">{count as number}</p>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="high_stakes">High Stakes ({highStakesCount})</TabsTrigger>
          <TabsTrigger value="ambiguous">Ambiguous (40-70)</TabsTrigger>
          <TabsTrigger value="senior">Senior Roles</TabsTrigger>
          <TabsTrigger value="follow_up">Follow-up Approvals</TabsTrigger>
          <TabsTrigger value="email_reply">Recruiter Replies</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">
          <ReviewQueue filterType="all" />
        </TabsContent>

        <TabsContent value="high_stakes" className="mt-6">
          <ReviewQueue filterType="all" />
        </TabsContent>

        <TabsContent value="ambiguous" className="mt-6">
          <ReviewQueue filterType="ambiguous" />
        </TabsContent>

        <TabsContent value="senior" className="mt-6">
          <ReviewQueue filterType="senior" />
        </TabsContent>

        <TabsContent value="follow_up" className="mt-6">
          <ReviewQueue filterType="follow_up" />
        </TabsContent>

        <TabsContent value="email_reply" className="mt-6">
          <ReviewQueue filterType="email_reply" />
        </TabsContent>
      </Tabs>
    </div>
  )
}