import React, { useState } from "react";
import axios from "axios";
import { Container, TextField, Button, List, ListItem, ListItemText, Typography, Paper, Box } from "@mui/material";

function ChatBot() {
  const [query, setQuery] = useState("");
  const [responses, setResponses] = useState([]);

  const handleQuery = async () => {
    if (!query.trim()) return;
    try {
      const response = await axios.post("http://localhost:8000/chatbot", { query });
      setResponses([...responses, { query, response: response.data.response }]);
      setQuery("");
    } catch (error) {
      console.error("Error fetching response:", error);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ display: "flex", flexDirection: "column", alignItems: "center", mt: 4 }}>
      <Paper elevation={3} sx={{ width: "100%", p: 3, borderRadius: 3, bgcolor: "#f4f6f8" }}>
        <Typography variant="h4" align="center" gutterBottom sx={{ fontWeight: "bold", color: "#1976d2" }}>
          AI-Powered Chatbot
        </Typography>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Enter your query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{ mt: 2, bgcolor: "white", borderRadius: 1 }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleQuery}
          sx={{ mt: 2, width: "100%", fontWeight: "bold", textTransform: "none" }}
        >
          Submit
        </Button>
        <Box sx={{ mt: 3, maxHeight: 300, overflowY: "auto", borderRadius: 2, p: 1, bgcolor: "white" }}>
          <List>
            {responses.map((item, index) => (
              <ListItem key={index} sx={{ display: "flex", flexDirection: "column", alignItems: "flex-start", mb: 2 }}>
                <ListItemText
                  primary={<Typography sx={{ fontWeight: "bold", color: "#333" }}>You: {item.query}</Typography>}
                />
                <ListItemText
                  secondary={<Typography sx={{ bgcolor: "#e3f2fd", p: 1, borderRadius: 2, color: "#000" }}>Chatbot: {item.response}</Typography>}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Paper>
    </Container>
  );
}

export default ChatBot;
