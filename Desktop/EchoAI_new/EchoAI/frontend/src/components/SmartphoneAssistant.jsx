import {
    useVoiceAssistant,
    BarVisualizer,
    VoiceAssistantControlBar,
    useTrackTranscription,
    useLocalParticipant,
  } from "@livekit/components-react";
  import { Track } from "livekit-client";
  import { useEffect, useState } from "react";
  import "./SmartphoneAssistant.css";
  
  const Message = ({ type, text }) => {
    return <div className={`message message-${type}`}>
      <div className="message-avatar">
        {type === "agent" ? "🤖" : "👤"}
      </div>
      <div className="message-content">
        <div className="message-sender">
          {type === "agent" ? "AI Assistant" : "You"}
        </div>
        <div className="message-text">{text}</div>
      </div>
    </div>;
  };
  
  const TaskApproval = ({ task, onApprove, onReject }) => {
    return (
      <div className="task-approval">
        <div className="task-details">
          <h4>Approval Required</h4>
          <p>{task}</p>
        </div>
        <div className="task-actions">
          <button className="approve-button" onClick={onApprove}>Approve</button>
          <button className="reject-button" onClick={onReject}>Reject</button>
        </div>
      </div>
    );
  };
  
  const SmartphoneAssistant = () => {
    const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
    const localParticipant = useLocalParticipant();
    const { segments: userTranscriptions } = useTrackTranscription({
      publication: localParticipant.microphoneTrack,
      source: Track.Source.Microphone,
      participant: localParticipant.localParticipant,
    });
  
    const [messages, setMessages] = useState([]);
    const [pendingTask, setPendingTask] = useState(null);
    const [taskHistory, setTaskHistory] = useState([]);
    const [activeStep, setActiveStep] = useState(0);
    const [taskSteps, setTaskSteps] = useState([]);
  
    // Simulate task detection from transcriptions
    useEffect(() => {
      if (agentTranscriptions && agentTranscriptions.length > 0) {
        const lastTranscription = agentTranscriptions[agentTranscriptions.length - 1].text;
        
        if (lastTranscription.includes("Would you like me to") || 
            lastTranscription.includes("Do you want me to") ||
            lastTranscription.includes("Should I")) {
          // Extract potential task
          const taskMatch = lastTranscription.match(/(?:Would you like me to|Do you want me to|Should I) (.*?)(?:\?|$)/i);
          if (taskMatch && taskMatch[1]) {
            setPendingTask(taskMatch[1].trim());
          }
        }
      }
    }, [agentTranscriptions]);
  
    // Combine all messages for display
    useEffect(() => {
      const allMessages = [
        ...(agentTranscriptions?.map((t) => ({ ...t, type: "agent" })) ?? []),
        ...(userTranscriptions?.map((t) => ({ ...t, type: "user" })) ?? []),
      ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
      setMessages(allMessages);
    }, [agentTranscriptions, userTranscriptions]);
  
    // Handle task approval
    const handleApproveTask = () => {
      if (pendingTask) {
        // Simulate generating task steps
        const steps = generateTaskSteps(pendingTask);
        setTaskSteps(steps);
        setActiveStep(0);
        
        // Add to task history
        setTaskHistory([...taskHistory, { task: pendingTask, status: 'in_progress' }]);
        setPendingTask(null);
      }
    };
  
    // Handle task rejection
    const handleRejectTask = () => {
      if (pendingTask) {
        setTaskHistory([...taskHistory, { task: pendingTask, status: 'rejected' }]);
        setPendingTask(null);
      }
    };
  
    // Simulate task step execution
    const executeNextStep = () => {
      if (activeStep < taskSteps.length - 1) {
        setActiveStep(activeStep + 1);
      } else {
        // Task completed
        const updatedHistory = [...taskHistory];
        updatedHistory[updatedHistory.length - 1].status = 'completed';
        setTaskHistory(updatedHistory);
        setTaskSteps([]);
        setActiveStep(0);
      }
    };
  
    // Simulate generating steps for a task
    const generateTaskSteps = (task) => {
      if (task.includes("switch")) {
        return [
          "Preparing to switch apps",
          "Checking currently running apps",
          "Switching to requested app",
          "App brought to foreground"
        ];
      } else if (task.includes("calendar") || task.includes("schedule")) {
        return [
          "Opening calendar application",
          "Checking for available time slots",
          "Creating new calendar event",
          "Setting reminder notification",
          "Event successfully added"
        ];
      } else if (task.includes("metrics") || task.includes("analysis")) {
        return [
          "Gathering device usage data",
          "Processing performance metrics",
          "Generating analysis report",
          "Preparing visualization of results"
        ];
      } else if (task.includes("transaction") || task.includes("payment")) {
        return [
          "Preparing secure transaction environment",
          "Validating payment details",
          "Confirming transaction amount",
          "Processing payment",
          "Verifying successful completion"
        ];
      } else {
        return [
          "Analyzing request",
          "Preparing execution plan",
          "Executing requested action",
          "Completing task"
        ];
      }
    };
  
    return (
      <div className="smartphone-assistant-container">
        <div className="visualizer-container">
          <BarVisualizer state={state} barCount={20} trackRef={audioTrack} />
        </div>
        
        <div className="assistant-main">
          <div className="conversation">
            {messages.map((msg, index) => (
              <Message key={msg.id || index} type={msg.type} text={msg.text} />
            ))}
          </div>
          
          {pendingTask && (
            <TaskApproval 
              task={pendingTask} 
              onApprove={handleApproveTask} 
              onReject={handleRejectTask} 
            />
          )}
          
          {taskSteps.length > 0 && (
            <div className="task-progress">
              <h4>Task Progress</h4>
              <div className="steps-container">
                {taskSteps.map((step, index) => (
                  <div 
                    key={index} 
                    className={`step ${index < activeStep ? 'completed' : ''} ${index === activeStep ? 'active' : ''}`}
                  >
                    <div className="step-number">{index + 1}</div>
                    <div className="step-text">{step}</div>
                  </div>
                ))}
              </div>
              {activeStep < taskSteps.length && (
                <button className="continue-button" onClick={executeNextStep}>
                  Continue
                </button>
              )}
            </div>
          )}
          
          <div className="task-history">
            <h4>Recent Tasks</h4>
            {taskHistory.length === 0 ? (
              <p className="no-tasks">No tasks executed yet</p>
            ) : (
              <ul className="task-list">
                {taskHistory.map((item, index) => (
                  <li key={index} className={`task-item task-${item.status}`}>
                    <span className="task-name">{item.task}</span>
                    <span className="task-status">
                      {item.status === 'completed' ? '✓ Completed' : 
                       item.status === 'rejected' ? '✗ Rejected' : '⋯ In Progress'}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        
        <div className="control-section">
          <VoiceAssistantControlBar />
        </div>
      </div>
    );
  };
  
  export default SmartphoneAssistant;