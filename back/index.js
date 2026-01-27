const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth');
const app = express();


app.use(cors()); // Enable CORS for all origins
app.use(express.json());

// Mount the auth routes
app.use('/api/auth', authRoutes);

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});