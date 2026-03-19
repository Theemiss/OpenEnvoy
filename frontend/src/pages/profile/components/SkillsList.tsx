import React, { useState } from 'react'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Badge } from '@/components/UI/Badge'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { PlusIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface SkillsListProps {
  skills: string[]
  languages: string[]
  tools: string[]
  onUpdate: (data: { skills: string[]; languages: string[]; tools: string[] }) => void
  isLoading?: boolean
}

export const SkillsList: React.FC<SkillsListProps> = ({
  skills = [],
  languages = [],
  tools = [],
  onUpdate,
  isLoading = false,
}) => {
  const [newSkill, setNewSkill] = useState('')
  const [newLanguage, setNewLanguage] = useState('')
  const [newTool, setNewTool] = useState('')

  const handleAddSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      onUpdate({
        skills: [...skills, newSkill.trim()],
        languages,
        tools,
      })
      setNewSkill('')
    }
  }

  const handleRemoveSkill = (skill: string) => {
    onUpdate({
      skills: skills.filter(s => s !== skill),
      languages,
      tools,
    })
  }

  const handleAddLanguage = () => {
    if (newLanguage.trim() && !languages.includes(newLanguage.trim())) {
      onUpdate({
        skills,
        languages: [...languages, newLanguage.trim()],
        tools,
      })
      setNewLanguage('')
    }
  }

  const handleRemoveLanguage = (language: string) => {
    onUpdate({
      skills,
      languages: languages.filter(l => l !== language),
      tools,
    })
  }

  const handleAddTool = () => {
    if (newTool.trim() && !tools.includes(newTool.trim())) {
      onUpdate({
        skills,
        languages,
        tools: [...tools, newTool.trim()],
      })
      setNewTool('')
    }
  }

  const handleRemoveTool = (tool: string) => {
    onUpdate({
      skills,
      languages,
      tools: tools.filter(t => t !== tool),
    })
  }

  const handleKeyPress = (e: React.KeyboardEvent, addFn: () => void) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addFn()
    }
  }

  return (
    <div className="space-y-6">
      {/* Technical Skills */}
      <Card>
        <CardHeader>
          <CardTitle>Technical Skills</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={(e) => handleKeyPress(e, handleAddSkill)}
                placeholder="Add a skill (e.g., Python, React)"
                className="flex-1"
              />
              <Button
                onClick={handleAddSkill}
                icon={<PlusIcon className="w-4 h-4" />}
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {skills.map((skill) => (
                <Badge key={skill} variant="info" size="md">
                  {skill}
                  <button
                    onClick={() => handleRemoveSkill(skill)}
                    className="ml-2 hover:text-red-600"
                  >
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
              {skills.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No skills added yet
                </p>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Languages */}
      <Card>
        <CardHeader>
          <CardTitle>Languages</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={newLanguage}
                onChange={(e) => setNewLanguage(e.target.value)}
                onKeyPress={(e) => handleKeyPress(e, handleAddLanguage)}
                placeholder="Add a language (e.g., English, Spanish)"
                className="flex-1"
              />
              <Button
                onClick={handleAddLanguage}
                icon={<PlusIcon className="w-4 h-4" />}
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {languages.map((language) => (
                <Badge key={language} variant="success" size="md">
                  {language}
                  <button
                    onClick={() => handleRemoveLanguage(language)}
                    className="ml-2 hover:text-red-600"
                  >
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
              {languages.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No languages added yet
                </p>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Tools */}
      <Card>
        <CardHeader>
          <CardTitle>Tools & Technologies</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={newTool}
                onChange={(e) => setNewTool(e.target.value)}
                onKeyPress={(e) => handleKeyPress(e, handleAddTool)}
                placeholder="Add a tool (e.g., Docker, AWS)"
                className="flex-1"
              />
              <Button
                onClick={handleAddTool}
                icon={<PlusIcon className="w-4 h-4" />}
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {tools.map((tool) => (
                <Badge key={tool} variant="warning" size="md">
                  {tool}
                  <button
                    onClick={() => handleRemoveTool(tool)}
                    className="ml-2 hover:text-red-600"
                  >
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
              {tools.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No tools added yet
                </p>
              )}
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default SkillsList