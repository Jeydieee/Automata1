document.addEventListener("DOMContentLoaded", fetchHistory);

async function scanMessage() {
    const message = document.getElementById('messageInput').value;
    const resultCard = document.getElementById('resultCard');
    const badge = document.getElementById('resultBadge');

    if (!message) return alert("Please enter a message!");

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        resultCard.style.display = 'block';

        // Update Badge
        if (data.is_spam) {
            badge.className = "badge spam";
            badge.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${data.classification}`;
        } else {
            badge.className = "badge safe";
            badge.innerHTML = `<i class="fas fa-check-circle"></i> ${data.classification}`;
        }

        // Update Stats
        document.getElementById('keywordsFound').innerText = data.patterns_found.length > 0 ? data.patterns_found.join(", ") : "None";
        document.getElementById('riskScore').innerText = data.heuristic_score + "%";

        // Visualize Automata Steps
        visualizeAutomata(data.automata_logs);

        // Refresh History
        fetchHistory();

    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong! Check the Console (F12) for details.");
    }
}

function visualizeAutomata(logs) {
    const container = document.getElementById('automataLog');
    container.innerHTML = ""; // Clear previous

    if (!logs || logs.length === 0) {
        container.innerHTML = "<p>No transition data available.</p>";
        return;
    }

    logs.forEach((log, index) => {
        const div = document.createElement('div');
        div.className = 'step';

        let arrow = "→";
        let color = "#34D399"; // Green for normal transition

        if (log.status.includes("MATCH")) color = "#EF4444"; // Red for match
        if (log.status === "Reset") color = "#6B7280"; // Grey for reset

        div.innerHTML = `
            <span style="color:#aaa">[${index}]</span> 
            State <strong>${log.from_state}</strong> 
            + Input '<strong>${log.char}</strong>' 
            ${arrow} State <strong>${log.to_state}</strong> 
            <span style="color:${color}">(${log.status})</span>
        `;
        container.appendChild(div);
    });

    // Auto scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function fetchHistory() {
    try {
        const response = await fetch('/history');
        if (!response.ok) return;

        const data = await response.json();
        const list = document.getElementById('historyList');
        list.innerHTML = "";

        data.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item[1]}</strong>: "${item[0].substring(0, 30)}..." <br><small>${item[3]}</small>`;
            list.appendChild(li);
        });
    } catch (error) {
        console.log("Could not fetch history:", error);
    }
}