import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8080';

export default function App() {
  const [employees, setEmployees] = useState([]);
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [activeRunId, setActiveRunId] = useState(null);
  const [polling, setPolling] = useState(false);
  const [message, setMessage] = useState('');
  const [newEmployee, setNewEmployee] = useState({ fullName: '', email: '', department: '' });

  // 1. Fetch employees on mount
  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await fetch(`${API_BASE}/employees`);
      if (res.ok) {
        const data = await res.json();
        setEmployees(data);
      }
    } catch (err) {
      console.error('Error fetching employees:', err);
    }
  };

  // 2. Poll workflow run every 2 seconds when activeRunId is set and polling is active
  useEffect(() => {
    if (!activeRunId || !polling) return;

    const intervalId = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/workflows/${activeRunId}`);
        if (res.ok) {
          const runData = await res.json();
          setActiveWorkflow(runData);

          // Stop polling once terminal status reached
          if (
            runData.status === 'COMPLETED' ||
            runData.status === 'FAILED_NEEDS_MANUAL_REVIEW'
          ) {
            setPolling(false);
            fetchEmployees(); // Refresh employee status in list
          }
        }
      } catch (err) {
        console.error('Error polling workflow:', err);
      }
    }, 2000);

    return () => clearInterval(intervalId);
  }, [activeRunId, polling]);

  // 3. Trigger Onboard workflow
  const handleOnboard = async (employeeId) => {
    setMessage(`Starting onboarding for employee #${employeeId}...`);
    try {
      const res = await fetch(`${API_BASE}/workflows/onboard/${employeeId}`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setActiveWorkflow(data);
        setActiveRunId(data.id);
        setPolling(true);
        setMessage(`Onboarding workflow #${data.id} initiated.`);
      } else {
        const errData = await res.json();
        setMessage(`Error: ${errData.message || 'Failed to start onboarding'}`);
      }
    } catch (err) {
      setMessage(`Error connecting to backend: ${err.message}`);
    }
  };

  // 4. Trigger Offboard workflow
  const handleOffboard = async (employeeId) => {
    setMessage(`Starting offboarding for employee #${employeeId}...`);
    try {
      const res = await fetch(`${API_BASE}/workflows/offboard/${employeeId}`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setActiveWorkflow(data);
        setActiveRunId(data.id);
        setPolling(true);
        setMessage(`Offboarding workflow #${data.id} initiated.`);
      } else {
        const errData = await res.json();
        setMessage(`Error: ${errData.message || 'Failed to start offboarding'}`);
      }
    } catch (err) {
      setMessage(`Error connecting to backend: ${err.message}`);
    }
  };

  // 5. Create new employee helper
  const handleCreateEmployee = async (e) => {
    e.preventDefault();
    if (!newEmployee.fullName || !newEmployee.email) return;

    try {
      const res = await fetch(`${API_BASE}/employees`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEmployee),
      });
      if (res.ok) {
        setNewEmployee({ fullName: '', email: '', department: '' });
        fetchEmployees();
        setMessage('Employee created successfully.');
      } else {
        const err = await res.json();
        setMessage(`Error: ${err.message || 'Failed to create employee'}`);
      }
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>IntegraFlow</h1>
        <p style={styles.subtitle}>Employee Onboarding & Offboarding Orchestration</p>
      </header>

      {message && <div style={styles.banner}>{message}</div>}

      <div style={styles.grid}>
        {/* Left Column: Employee List & Form */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>Employees</h2>
            <button style={styles.btnSecondary} onClick={fetchEmployees}>Refresh</button>
          </div>

          <table style={styles.table}>
            <thead>
              <tr style={styles.thRow}>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Email</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '16px' }}>No employees found.</td>
                </tr>
              ) : (
                employees.map((emp) => (
                  <tr key={emp.id} style={styles.tr}>
                    <td style={styles.td}>{emp.id}</td>
                    <td style={styles.td}><strong>{emp.fullName}</strong></td>
                    <td style={styles.td}>{emp.email}</td>
                    <td style={styles.td}>
                      <span style={emp.status === 'ACTIVE' ? styles.badgeActive : styles.badgeInactive}>
                        {emp.status}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <button
                        style={styles.btnOnboard}
                        onClick={() => handleOnboard(emp.id)}
                        disabled={polling}
                      >
                        Onboard
                      </button>
                      <button
                        style={styles.btnOffboard}
                        onClick={() => handleOffboard(emp.id)}
                        disabled={polling}
                      >
                        Offboard
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Quick Add Employee */}
          <form onSubmit={handleCreateEmployee} style={styles.form}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#4b5563' }}>Add New Employee</h3>
            <div style={styles.formRow}>
              <input
                type="text"
                placeholder="Full Name"
                value={newEmployee.fullName}
                onChange={(e) => setNewEmployee({ ...newEmployee, fullName: e.target.value })}
                style={styles.input}
                required
              />
              <input
                type="email"
                placeholder="Email Address"
                value={newEmployee.email}
                onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
                style={styles.input}
                required
              />
              <input
                type="text"
                placeholder="Department"
                value={newEmployee.department}
                onChange={(e) => setNewEmployee({ ...newEmployee, department: e.target.value })}
                style={styles.input}
              />
              <button type="submit" style={styles.btnAdd}>+ Add</button>
            </div>
          </form>
        </div>

        {/* Right Column: Live Workflow Monitoring Panel */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>Live Workflow Execution</h2>
            {polling && <span style={styles.pollingBadge}>● Live Polling (2s)</span>}
          </div>

          {!activeWorkflow ? (
            <div style={styles.emptyPanel}>
              <p>No active workflow. Click <strong>Onboard</strong> or <strong>Offboard</strong> on an employee to watch orchestration in real time.</p>
            </div>
          ) : (
            <div>
              <div style={styles.runSummary}>
                <div><strong>Run ID:</strong> #{activeWorkflow.id}</div>
                <div><strong>Type:</strong> {activeWorkflow.workflowType}</div>
                <div>
                  <strong>Status:</strong>{' '}
                  <span style={getStatusBadgeStyle(activeWorkflow.status)}>
                    {activeWorkflow.status}
                  </span>
                </div>
              </div>

              <h4 style={{ margin: '16px 0 8px 0', fontSize: '13px', color: '#6b7280', textTransform: 'uppercase' }}>
                Workflow Steps ({activeWorkflow.steps?.length || 0})
              </h4>

              <div style={styles.stepsList}>
                {activeWorkflow.steps && activeWorkflow.steps.map((step) => (
                  <div key={step.id || step.stepOrder} style={styles.stepCard}>
                    <div style={styles.stepHeader}>
                      <span style={styles.stepNumber}>Step {step.stepOrder}</span>
                      <strong style={styles.stepName}>{step.stepName}</strong>
                      <span style={styles.stepIntegration}>[{step.integrationType}]</span>
                      <span style={getStepBadgeStyle(step.status)}>
                        {step.status}
                      </span>
                    </div>
                    {step.errorMessage && (
                      <div style={styles.stepError}>Error: {step.errorMessage}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getStatusBadgeStyle(status) {
  if (status === 'COMPLETED') return styles.badgeSuccess;
  if (status === 'FAILED_NEEDS_MANUAL_REVIEW') return styles.badgeFailed;
  return styles.badgePending;
}

function getStepBadgeStyle(status) {
  if (status === 'SUCCESS') return styles.badgeSuccess;
  if (status === 'FAILED') return styles.badgeFailed;
  return styles.badgePending;
}

const styles = {
  container: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px 16px',
    color: '#1f2937',
    backgroundColor: '#f9fafb',
    minHeight: '100vh',
  },
  header: {
    marginBottom: '24px',
    borderBottom: '2px solid #e5e7eb',
    paddingBottom: '16px',
  },
  title: {
    margin: '0 0 4px 0',
    fontSize: '28px',
    fontWeight: '700',
    color: '#111827',
  },
  subtitle: {
    margin: '0',
    fontSize: '14px',
    color: '#6b7280',
  },
  banner: {
    backgroundColor: '#e0f2fe',
    color: '#0369a1',
    border: '1px solid #bae6fd',
    borderRadius: '6px',
    padding: '10px 14px',
    marginBottom: '20px',
    fontSize: '14px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    border: '1px solid #e5e7eb',
    padding: '20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
    borderBottom: '1px solid #f3f4f6',
    paddingBottom: '8px',
  },
  cardTitle: {
    margin: 0,
    fontSize: '18px',
    fontWeight: '600',
  },
  pollingBadge: {
    fontSize: '12px',
    color: '#059669',
    fontWeight: '600',
    backgroundColor: '#d1fae5',
    padding: '3px 8px',
    borderRadius: '12px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '13px',
    marginBottom: '20px',
  },
  thRow: {
    backgroundColor: '#f9fafb',
    textAlign: 'left',
  },
  th: {
    padding: '10px 8px',
    borderBottom: '1px solid #e5e7eb',
    color: '#4b5563',
    fontWeight: '600',
  },
  tr: {
    borderBottom: '1px solid #f3f4f6',
  },
  td: {
    padding: '10px 8px',
  },
  badgeActive: {
    backgroundColor: '#d1fae5',
    color: '#065f46',
    padding: '2px 8px',
    borderRadius: '10px',
    fontSize: '11px',
    fontWeight: '600',
  },
  badgeInactive: {
    backgroundColor: '#f3f4f6',
    color: '#6b7280',
    padding: '2px 8px',
    borderRadius: '10px',
    fontSize: '11px',
    fontWeight: '600',
  },
  badgeSuccess: {
    backgroundColor: '#d1fae5',
    color: '#065f46',
    padding: '3px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '600',
  },
  badgeFailed: {
    backgroundColor: '#fee2e2',
    color: '#991b1b',
    padding: '3px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '600',
  },
  badgePending: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
    padding: '3px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '600',
  },
  btnOnboard: {
    backgroundColor: '#2563eb',
    color: '#ffffff',
    border: 'none',
    borderRadius: '4px',
    padding: '5px 9px',
    fontSize: '12px',
    cursor: 'pointer',
    marginRight: '6px',
  },
  btnOffboard: {
    backgroundColor: '#dc2626',
    color: '#ffffff',
    border: 'none',
    borderRadius: '4px',
    padding: '5px 9px',
    fontSize: '12px',
    cursor: 'pointer',
  },
  btnSecondary: {
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    padding: '4px 10px',
    fontSize: '12px',
    cursor: 'pointer',
  },
  form: {
    backgroundColor: '#f9fafb',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
  },
  formRow: {
    display: 'flex',
    gap: '8px',
  },
  input: {
    flex: 1,
    padding: '6px 8px',
    fontSize: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
  },
  btnAdd: {
    backgroundColor: '#10b981',
    color: '#ffffff',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 12px',
    fontSize: '12px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  emptyPanel: {
    padding: '40px 20px',
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: '14px',
  },
  runSummary: {
    display: 'flex',
    justifyContent: 'space-between',
    backgroundColor: '#f3f4f6',
    padding: '12px 16px',
    borderRadius: '6px',
    fontSize: '13px',
    marginBottom: '16px',
  },
  stepsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  stepCard: {
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    padding: '10px 12px',
    backgroundColor: '#ffffff',
  },
  stepHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
  },
  stepNumber: {
    color: '#6b7280',
    fontSize: '11px',
    fontWeight: '600',
  },
  stepName: {
    flex: 1,
  },
  stepIntegration: {
    color: '#9ca3af',
    fontSize: '11px',
  },
  stepError: {
    marginTop: '6px',
    color: '#b91c1c',
    fontSize: '12px',
    backgroundColor: '#fef2f2',
    padding: '4px 8px',
    borderRadius: '4px',
  },
};
