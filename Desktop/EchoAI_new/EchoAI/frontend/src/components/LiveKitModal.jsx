// import { useState, useCallback } from "react";
// import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
// import "@livekit/components-styles";
// import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

// const LiveKitModal = ({ setShowSupport }) => {
//   const [isSubmittingName, setIsSubmittingName] = useState(true);
//   const [name, setName] = useState("");
//   const [token, setToken] = useState(null);

//   const getToken = useCallback(async (userName) => {
//     try {
//       console.log("run")
//       const response = await fetch(
//         `/api/getToken?name=${encodeURIComponent(userName)}`
//       );
//       const token = await response.text();
//       setToken(token);
//       setIsSubmittingName(false);
//     } catch (error) {
//       console.error(error);
//     }
//   }, []);

//   const handleNameSubmit = (e) => {
//     e.preventDefault();
//     if (name.trim()) {
//       getToken(name);
//     }
//   };

//   return (
//     <div className="modal-overlay">
//       <div className="modal-content">
//         <div className="support-room">
//           {isSubmittingName ? (
//             <form onSubmit={handleNameSubmit} className="name-form">
//               <h2>Enter your name to connect with support</h2>
//               <input
//                 type="text"
//                 value={name}
//                 onChange={(e) => setName(e.target.value)}
//                 placeholder="Your name"
//                 required
//               />
//               <button type="submit">Connect</button>
//               <button
//                 type="button"
//                 className="cancel-button"
//                 onClick={() => setShowSupport(false)}
//               >
//                 Cancel
//               </button>
//             </form>
//           ) : token ? (
//             <LiveKitRoom
//               serverUrl={import.meta.env.VITE_LIVEKIT_URL}
//               token={token}
//               connect={true}
//               video={false}
//               audio={true}
//               onDisconnected={() => {
//                 setShowSupport(false);
//                 setIsSubmittingName(true);
//               }}
//             >
//               <RoomAudioRenderer />
//               <SimpleVoiceAssistant />
//             </LiveKitRoom>
//           ) : null}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default LiveKitModal;
// LiveKitModal.jsx
import { useState, useCallback } from "react";
import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import SmartphoneAssistant from "./SmartphoneAssistant";

const LiveKitModal = ({ setShowSupport }) => {
  const [isSubmittingName, setIsSubmittingName] = useState(true);
  const [name, setName] = useState("");
  const [token, setToken] = useState(null);

  const getToken = useCallback(async (userName) => {
    try {
      const response = await fetch(
        `/api/getToken?name=${encodeURIComponent(userName)}`
      );
      const token = await response.text();
      setToken(token);
      setIsSubmittingName(false);
    } catch (error) {
      console.error("Error fetching token:", error);
    }
  }, []);

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      getToken(name);
    }
  };

  const handleClose = () => {
    setShowSupport(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-button" onClick={handleClose}>×</button>
        <div className="support-room">
          {isSubmittingName ? (
            <form onSubmit={handleNameSubmit} className="name-form">
              <h2>Enter your name to connect with AI Assistant</h2>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
              <button type="submit">Connect</button>
              <button
                type="button"
                className="cancel-button"
                onClick={handleClose}
              >
                Cancel
              </button>
            </form>
          ) : token ? (
            <LiveKitRoom
              serverUrl={import.meta.env.VITE_LIVEKIT_URL}
              token={token}
              connect={true}
              video={false}
              audio={true}
              onDisconnected={() => {
                setShowSupport(false);
                setIsSubmittingName(true);
              }}
            >
              <RoomAudioRenderer />
              <SmartphoneAssistant />
            </LiveKitRoom>
          ) : (
            <div className="loading">Connecting to AI Assistant...</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveKitModal;