// import express from 'express';
// import dotenv from 'dotenv';
// import apiRoutes from './src/routes/apiRoutes.js';

// dotenv.config();

// const app = express();
// const PORT = process.env.PORT;

// app.use(express.json());

// app.use('/api', apiRoutes);

// app.use((err, req, res, next) => {
//     console.error(err.stack);
//     res.status(500).json({ error: 'Something broke!' });
// });

// app.listen(PORT, () => {
//     console.log(`Node.js backend running on http://localhost:${PORT}`);
//     console.log(`Forwarding requests to Python service at ${process.env.PYTHON_API_URL}`);
// });
import express from 'express';
import dotenv from 'dotenv';
import apiRoutes from './src/routes/apiRoutes.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT;


app.use(express.json());

// Routes
app.use('/api', apiRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something broke!' });
});

import os from 'os';

// function getLocalIP() {
//   const nets = os.networkInterfaces();
//   for (const name of Object.keys(nets)) {
//     for (const net of nets[name] || []) {
//       if (net.family === 'IPv4' && !net.internal) {
//         return net.address; // مثل 192.168.1.10
//       }
//     }
//   }
//   return 'YOUR_LAN_IP';
// }

// function getLanIP() {
//   const nets = os.networkInterfaces();

//   const preferred = [
//     'Wi-Fi',
//     'Wireless LAN adapter Wi-Fi',
//     'Ethernet',
//     'Local Area Connection',
//   ];

//   // جرّب واجهات الشبكة الشائعة أولاً
//   for (const key of Object.keys(nets)) {
//     const isPreferred = preferred.some(p => key.toLowerCase().includes(p.toLowerCase()));
//     if (!isPreferred) continue;

//     for (const net of nets[key] || []) {
//       if (net.family === 'IPv4' && !net.internal) return net.address;
//     }
//   }

//   // إذا ما لقى، رجّع أول IPv4 لكن تجاهل الشبكات الافتراضية المشهورة
//   const skipIfNameHas = ['vpn', 'docker', 'wsl', 'hyper-v', 'virtual', 'vmware', 'vbox', 'loopback', 'tunnel'];
//   for (const name of Object.keys(nets)) {
//     if (skipIfNameHas.some(s => name.toLowerCase().includes(s))) continue;

//     for (const net of nets[name] || []) {
//       if (net.family === 'IPv4' && !net.internal) return net.address;
//     }
//   }

//   return null;
// }


// const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

// app.listen(PORT, HOST, () => {
//   console.log(`Local:   http://localhost:${PORT}`);
//   console.log(`LAN:     http://${getLocalIP()}:${PORT}`);
// });
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Node.js backend running on http://localhost:${PORT}`);
  console.log(`Forwarding requests to Python service at ${process.env.PYTHON_API_URL}`);
});

// app.listen(PORT, '0.0.0.0', () => {
//   console.log(`Local: http://localhost:${PORT}`);

//   const nets = os.networkInterfaces();
//   let lanIP = null;

//   for (const name of Object.keys(nets)) {
//     for (const net of nets[name] || []) {
//       if (
//         net.family === 'IPv4' &&
//         !net.internal &&
//         !name.toLowerCase().includes('vpn') &&
//         !name.toLowerCase().includes('docker') &&
//         !name.toLowerCase().includes('wsl') &&
//         !name.toLowerCase().includes('hyper') &&
//         !name.toLowerCase().includes('virtual')
//       ) {
//         lanIP = net.address;
//         break;
//       }
//     }
//     if (lanIP) break;
//   }

//   if (lanIP) {
//     console.log(`LAN:   http://${lanIP}:${PORT}`);
//   } else {
//     console.log('LAN:   could not detect LAN IP');
//   }

//   console.log(`Python: ${process.env.PYTHON_API_URL}`);
// });




// app.listen(PORT, () => {
//     console.log(`Node.js backend running on http://localhost:${PORT}`);
//     console.log(`Forwarding requests to Python service at ${process.env.PYTHON_API_URL}`);
// });