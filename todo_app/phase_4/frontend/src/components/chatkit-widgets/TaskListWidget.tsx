/**
 * ChatKit Task List Widget
 * Uses ChatKit Studio components for rendering inside ChatKit sandbox
 */

import React from "react";

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: "low" | "medium" | "high";
  due_date?: string;
}

interface TaskListWidgetProps {
  tasks: Task[];
  title?: string;
}

/**
 * TaskListWidget - Renders tasks using ChatKit Studio components
 * Components available: Box, Row, Col, Text, Title, Caption, Checkbox, Badge, Icon, Divider
 */
export function TaskListWidget({ tasks, title = "Your Tasks" }: TaskListWidgetProps) {
  // Import ChatKit components dynamically (they're injected by ChatKit runtime)
  const Box = (globalThis as any).Box;
  const Row = (globalThis as any).Row;
  const Col = (globalThis as any).Col;
  const Text = (globalThis as any).Text;
  const Title = (globalThis as any).Title;
  const Caption = (globalThis as any).Caption;
  const Checkbox = (globalThis as any).Checkbox;
  const Badge = (globalThis as any).Badge;
  const Icon = (globalThis as any).Icon;
  const Divider = (globalThis as any).Divider;

  // Fallback for missing components
  if (!Box || !Row || !Col) {
    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <p className="text-gray-600">ChatKit components not available</p>
      </div>
    );
  }

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case "high": return "error";
      case "medium": return "warning";
      case "low": return "success";
      default: return "default";
    }
  };

  if (tasks.length === 0) {
    return (
      <Box padding={4} background="surface-secondary">
        <Col gap={2}>
          <Icon name="circle" size="lg" />
          <Text value="No tasks found" size="md" />
        </Col>
      </Box>
    );
  }

  const completedCount = tasks.filter(t => t.completed).length;
  const totalCount = tasks.length;
  const completionPercent = Math.round((completedCount / totalCount) * 100);

  return (
    <Box padding={4} background="surface">
      <Col gap={3}>
        {/* Header with title and stats */}
        <Row gap={2}>
          <Title value={title} size="lg" />
          <Badge label={`${completedCount}/${totalCount}`} color="primary" size="md" />
        </Row>

        <Caption value={`${completionPercent}% completed`} size="sm" />
        <Divider spacing={2} />

        {/* Task list */}
        {tasks.map((task, index) => (
          <React.Fragment key={task.id}>
            <Box padding={3} background="surface-secondary">
              <Col gap={2}>
                {/* Title row with checkbox and priority */}
                <Row gap={2}>
                  {task.completed ? (
                    <Icon name="check-circle-filled" size="md" />
                  ) : (
                    <Icon name="circle" size="md" />
                  )}
                  <Text
                    value={task.title}
                    size="md"
                  />
                  {task.priority && (
                    <Badge
                      label={task.priority.toUpperCase()}
                      color={getPriorityColor(task.priority)}
                      size="sm"
                    />
                  )}
                </Row>

                {/* Description */}
                {task.description && (
                  <Caption value={task.description} size="sm" />
                )}

                {/* Due date */}
                {task.due_date && (
                  <Row gap={1}>
                    <Icon name="calendar" size="sm" />
                    <Caption
                      value={`Due: ${new Date(task.due_date).toLocaleDateString()}`}
                      size="sm"
                    />
                  </Row>
                )}
              </Col>
            </Box>

            {index < tasks.length - 1 && <Divider spacing={1} />}
          </React.Fragment>
        ))}
      </Col>
    </Box>
  );
}
