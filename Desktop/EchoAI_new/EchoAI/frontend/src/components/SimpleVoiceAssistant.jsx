// import {
//   useVoiceAssistant,
//   BarVisualizer,
//   VoiceAssistantControlBar,
//   useTrackTranscription,
//   useLocalParticipant,
// } from "@livekit/components-react";
// import { Track } from "livekit-client";
// import { useEffect, useState } from "react";
// import "./SimpleVoiceAssistant.css";

// const Message = ({ type, text }) => {
//   return <div className="message">
//     <strong className={`message-${type}`}>
//       {type === "agent" ? "Agent: " : "You: "}
//     </strong>
//     <span className="message-text">{text}</span>
//   </div>;
// };

// const SimpleVoiceAssistant = () => {
//   const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
//   const localParticipant = useLocalParticipant();
//   const { segments: userTranscriptions } = useTrackTranscription({
//     publication: localParticipant.microphoneTrack,
//     source: Track.Source.Microphone,
//     participant: localParticipant.localParticipant,
//   });

//   const [messages, setMessages] = useState([]);

//   useEffect(() => {
//     const allMessages = [
//       ...(agentTranscriptions?.map((t) => ({ ...t, type: "agent" })) ?? []),
//       ...(userTranscriptions?.map((t) => ({ ...t, type: "user" })) ?? []),
//     ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
//     setMessages(allMessages);
//   }, [agentTranscriptions, userTranscriptions]);

//   return (
//     <div className="voice-assistant-container">
//       <div className="visualizer-container">
//         <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
//       </div>
//       <div className="control-section">
//         <VoiceAssistantControlBar />
//         <div className="conversation">
//           {messages.map((msg, index) => (
//             <Message key={msg.id || index} type={msg.type} text={msg.text} />
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default SimpleVoiceAssistant;
// SimpleVoiceAssistant.jsx
import {
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
  useTrackTranscription,
  useLocalParticipant,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState, useRef } from "react";
import "./SimpleVoiceAssistant.css";

const Message = ({ type, text }) => {
  return <div className={`message message-${type}`}>
    <strong className={`message-label`}>
      {type === "agent" ? "Assistant: " : "You: "}
    </strong>
    <span className="message-text">{text}</span>
  </div>;
};

const ActionButton = ({ text, onClick, type }) => {
  return (
    <button 
      className={`action-button ${type || "neutral"}`} 
      onClick={onClick}
    >
      {text}
    </button>
  );
};

const SimpleVoiceAssistant = () => {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const localParticipant = useLocalParticipant();
  const { segments: userTranscriptions } = useTrackTranscription({
    publication: localParticipant.microphoneTrack,
    source: Track.Source.Microphone,
    participant: localParticipant.localParticipant,
  });

  const [messages, setMessages] = useState([]);
  const [pendingActions, setPendingActions] = useState([]);
  const [currentApp, setCurrentApp] = useState("Home");
  const [isListening, setIsListening] = useState(false);
  const [userInput, setUserInput] = useState("");
  const conversationRef = useRef(null);

  // Simulate task execution and approval process
  const simulateTaskExecution = (taskText) => {
    // In a real implementation, this would be parsed from agent responses
    if (taskText.toLowerCase().includes("transaction")) {
      setPendingActions([
        {
          id: Date.now(),
          type: "transaction",
          description: "Payment of $25.99 to AutoZone for oil change",
          approveAction: () => handleApprove(Date.now()),
          rejectAction: () => handleReject(Date.now())
        }
      ]);
    }
  };

  const handleApprove = (actionId) => {
    // Add a system message showing approval
    const newMessage = {
      id: Date.now().toString(),
      type: "system",
      text: "✅ Action approved",
      firstReceivedTime: Date.now()
    };
    setMessages(prev => [...prev, newMessage]);
    setPendingActions([]);
    
    // Simulate agent response to approval
    setTimeout(() => {
      const agentResponse = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        text: "Transaction completed successfully. The payment has been processed.",
        firstReceivedTime: Date.now() + 1
      };
      setMessages(prev => [...prev, agentResponse]);
    }, 1000);
  };

  const handleReject = (actionId) => {
    // Add a system message showing rejection
    const newMessage = {
      id: Date.now().toString(),
      type: "system",
      text: "❌ Action rejected",
      firstReceivedTime: Date.now()
    };
    setMessages(prev => [...prev, newMessage]);
    setPendingActions([]);
    
    // Simulate agent response to rejection
    setTimeout(() => {
      const agentResponse = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        text: "Transaction cancelled. No payment was processed.",
        firstReceivedTime: Date.now() + 1
      };
      setMessages(prev => [...prev, agentResponse]);
    }, 1000);
  };

  const handleSendMessage = () => {
    if (!userInput.trim()) return;
    
    // Add user message to conversation
    const newMessage = {
      id: Date.now().toString(),
      type: "user",
      text: userInput,
      firstReceivedTime: Date.now()
    };
    setMessages(prev => [...prev, newMessage]);
    
    // Check if it's a task execution request
    if (userInput.toLowerCase().includes("payment") || 
        userInput.toLowerCase().includes("transaction") ||
        userInput.toLowerCase().includes("send money")) {
      simulateTaskExecution(userInput);
    }
    
    // Clear input
    setUserInput("");
  };

  const toggleListening = () => {
    setIsListening(!isListening);
  };

  useEffect(() => {
    const allMessages = [
      ...(agentTranscriptions?.map((t) => ({ ...t, type: "agent" })) ?? []),
      ...(userTranscriptions?.map((t) => ({ ...t, type: "user" })) ?? []),
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
    setMessages(allMessages);
    
    // Auto-scroll to bottom of conversation
    if (conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
  }, [agentTranscriptions, userTranscriptions]);

  return (
    <div className="voice-assistant-container">
      <div className="app-header">
        <div className="current-app">
          <span>Current App: {currentApp}</span>
        </div>
        <div className="app-icons">
          <button className="app-icon" onClick={() => setCurrentApp("Home")}>🏠</button>
          <button className="app-icon" onClick={() => setCurrentApp("Calendar")}>📅</button>
          <button className="app-icon" onClick={() => setCurrentApp("Messages")}>✉️</button>
          <button className="app-icon" onClick={() => setCurrentApp("Maps")}>🗺️</button>
          <button className="app-icon" onClick={() => setCurrentApp("Settings")}>⚙️</button>
        </div>
      </div>

      <div className="visualizer-container">
        <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
      </div>
      
      <div className="control-section">
        <VoiceAssistantControlBar />
        
        <div className="conversation" ref={conversationRef}>
          {messages.map((msg, index) => (
            <Message key={msg.id || index} type={msg.type} text={msg.text} />
          ))}
          
          {pendingActions.length > 0 && (
            <div className="pending-actions">
              <div className="pending-action-header">
                <h3>Approval Required</h3>
              </div>
              {pendingActions.map(action => (
                <div key={action.id} className="pending-action">
                  <p>{action.description}</p>
                  <div className="action-buttons">
                    <ActionButton text="Approve" onClick={action.approveAction} type="approve" />
                    <ActionButton text="Reject" onClick={action.rejectAction} type="reject" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="input-section">
          <input 
            type="text" 
            value={userInput} 
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type a message..."
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            className="text-input"
          />
          <button className="send-button" onClick={handleSendMessage}>Send</button>
          <button 
            className={`voice-button ${isListening ? 'listening' : ''}`} 
            onClick={toggleListening}
          >
            {isListening ? '🔴 Stop' : '🎤 Speak'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SimpleVoiceAssistant;