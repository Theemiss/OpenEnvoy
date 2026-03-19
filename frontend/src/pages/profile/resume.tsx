import React from 'react'
import { useRouter } from 'next/router'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Spinner } from '@/components/UI/Spinner'
import { Badge } from '@/components/UI/Badge'
import { profileApi } from '@/lib/api/client'
import {
  ArrowLeftIcon,
  CloudArrowDownIcon,
  PrinterIcon,
} from '@heroicons/react/24/outline'
import Link from 'next/link'

export default function ResumeDetailPage() {
  const router = useRouter()
  const { id } = router.query

  const { data: resumes, isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => profileApi.getResumes(),
  })

  const resume = resumes?.data?.find((r: any) => r.id === Number(id))
  const canonicalResume = resumes?.data?.find((r: any) => r.is_canonical)

  const handleDownload = () => {
    const content = resume?.content_json || resume
    if (!content) return
    const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${resume.name || `resume-${id}`}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  const handlePrint = () => {
    window.print()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!resume) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Resume not found
        </h2>
        <Link href="/profile" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          ← Back to Profile
        </Link>
      </div>
    )
  }

  const canonicalSkills: string[] = canonicalResume?.content_json?.skills || []
  const tailoredSkills: string[] = resume.content_json?.skills || []
  const addedSkills = tailoredSkills.filter((skill) => !canonicalSkills.includes(skill))
  const removedSkills = canonicalSkills.filter((skill) => !tailoredSkills.includes(skill))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/profile"
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {resume.name}
          </h1>
          {resume.is_canonical && (
            <Badge variant="success">Canonical</Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            icon={<PrinterIcon className="w-4 h-4" />}
            onClick={handlePrint}
          >
            Print
          </Button>
          <Button
            variant="primary"
            icon={<CloudArrowDownIcon className="w-4 h-4" />}
            onClick={handleDownload}
          >
            Download
          </Button>
        </div>
      </div>

      {/* Resume Content */}
      <Card>
        <CardBody>
          <div className="prose dark:prose-invert max-w-none">
            {/* Personal Info */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold">{resume.content_json?.personal?.name}</h1>
              <p className="text-gray-600 dark:text-gray-400">
                {resume.content_json?.personal?.email} • {resume.content_json?.personal?.phone}
              </p>
              {resume.content_json?.personal?.location && (
                <p className="text-gray-600 dark:text-gray-400">
                  {resume.content_json.personal.location}
                </p>
              )}
            </div>

            {/* Summary */}
            {resume.content_json?.summary && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-3">Professional Summary</h2>
                <p className="text-gray-700 dark:text-gray-300">
                  {resume.content_json.summary}
                </p>
              </div>
            )}

            {/* Skills */}
            {resume.content_json?.skills && resume.content_json.skills.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-3">Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {resume.content_json.skills.map((skill: string) => (
                    <Badge key={skill} variant="info">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Experience */}
            {resume.content_json?.experience && resume.content_json.experience.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Experience</h2>
                <div className="space-y-6">
                  {resume.content_json.experience.map((exp: any, index: number) => (
                    <div key={index}>
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium">{exp.title}</h3>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {exp.start_date} - {exp.end_date || 'Present'}
                        </span>
                      </div>
                      <p className="text-primary-600 dark:text-primary-400">{exp.company}</p>
                      {exp.description && (
                        <p className="mt-2 text-gray-700 dark:text-gray-300">
                          {exp.description}
                        </p>
                      )}
                      {exp.achievements && exp.achievements.length > 0 && (
                        <ul className="mt-2 list-disc list-inside text-gray-700 dark:text-gray-300">
                          {exp.achievements.map((ach: string, i: number) => (
                            <li key={i}>{ach}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {resume.content_json?.education && resume.content_json.education.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Education</h2>
                <div className="space-y-4">
                  {resume.content_json.education.map((edu: any, index: number) => (
                    <div key={index}>
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium">{edu.degree} in {edu.field}</h3>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {edu.start_date} - {edu.end_date}
                        </span>
                      </div>
                      <p className="text-gray-600 dark:text-gray-400">{edu.institution}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Projects */}
            {resume.content_json?.projects && resume.content_json.projects.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Projects</h2>
                <div className="space-y-4">
                  {resume.content_json.projects.map((proj: any, index: number) => (
                    <div key={index}>
                      <h3 className="text-lg font-medium">{proj.name}</h3>
                      <p className="text-gray-700 dark:text-gray-300 mt-1">
                        {proj.description}
                      </p>
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {proj.technologies.map((tech: string) => (
                            <Badge key={tech} variant="info" size="sm">
                              {tech}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {!resume.is_canonical && (
        <Card>
          <CardHeader>
            <CardTitle>Tailoring Diff Summary</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-3 text-sm">
              <p className="text-gray-600 dark:text-gray-400">
                Compared with the current canonical resume version.
              </p>
              <div>
                <p className="font-medium">Added skills emphasis</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {addedSkills.length === 0 ? (
                    <span className="text-gray-500 dark:text-gray-400">No added skills</span>
                  ) : (
                    addedSkills.map((skill) => (
                      <Badge key={skill} variant="success" size="sm">
                        + {skill}
                      </Badge>
                    ))
                  )}
                </div>
              </div>
              <div>
                <p className="font-medium">De-emphasized skills</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {removedSkills.length === 0 ? (
                    <span className="text-gray-500 dark:text-gray-400">No removed skills</span>
                  ) : (
                    removedSkills.map((skill) => (
                      <Badge key={skill} variant="warning" size="sm">
                        - {skill}
                      </Badge>
                    ))
                  )}
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}