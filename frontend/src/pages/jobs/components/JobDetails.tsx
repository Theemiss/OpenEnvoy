import React from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import { Job } from '@/lib/types/job'

interface JobDetailsProps {
  job: Job
}

export const JobDetails: React.FC<JobDetailsProps> = ({ job }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{job.title}</CardTitle>
      </CardHeader>
      <CardBody>
        <div className="prose dark:prose-invert max-w-none">
          {/* Job Description */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Description</h3>
            <div 
              className="text-gray-700 dark:text-gray-300"
              dangerouslySetInnerHTML={{ 
                __html: job.description_html || job.description.replace(/\n/g, '<br/>') 
              }}
            />
          </div>

          {/* Requirements */}
          {job.requirements && job.requirements.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">Requirements</h3>
              <ul className="list-disc list-inside space-y-2">
                {job.requirements.map((req, index) => (
                  <li key={index} className="text-gray-700 dark:text-gray-300">
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Benefits */}
          {job.benefits && job.benefits.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">Benefits</h3>
              <ul className="list-disc list-inside space-y-2">
                {job.benefits.map((benefit, index) => (
                  <li key={index} className="text-gray-700 dark:text-gray-300">
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Skills */}
          {job.skills && job.skills.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.skills.map((skill) => (
                  <Badge key={skill} variant="info">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  )
}

export default JobDetails