import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout.tsx';
import { Dashboard } from './pages/Dashboard.tsx';
import { AgentProfile } from './pages/AgentProfile.tsx';
import { AgentCommunication } from './pages/AgentCommunication.tsx';
import { TrustLogs } from './pages/TrustLogs.tsx';
import { CreateAgent } from './pages/CreateAgent.tsx';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agents/create" element={<CreateAgent />} />
          <Route path="/agents/:agentId" element={<AgentProfile />} />
          <Route path="/communication" element={<AgentCommunication />} />
          <Route path="/trust-logs" element={<TrustLogs />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
