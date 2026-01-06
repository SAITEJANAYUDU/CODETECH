const http = require('http');
const url = require('url');


class AdvancedCache {
  constructor() {
    this.store = new Map();
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0
    };
  }
  
  set(key, value, ttl = 30000) {
    this.store.set(key, {
      data: value,
      expiry: Date.now() + ttl
    });
    this.stats.sets++;
    return true;
  }
  
  get(key) {
    const item = this.store.get(key);
    if (!item) {
      this.stats.misses++;
      return null;
    }
    
    if (Date.now() > item.expiry) {
      this.store.delete(key);
      this.stats.misses++;
      return null;
    }
    
    this.stats.hits++;
    return item.data;
  }
  
  delete(key) {
    const deleted = this.store.delete(key);
    if (deleted) this.stats.deletes++;
    return deleted;
  }
  
  clear() {
    this.store.clear();
    this.stats = { hits: 0, misses: 0, sets: 0, deletes: 0 };
  }
  
  getStats() {
    const total = this.stats.hits + this.stats.misses;
    return {
      ...this.stats,
      size: this.store.size,
      hitRate: total > 0 ? ((this.stats.hits / total) * 100).toFixed(2) + '%' : '0%'
    };
  }
}

const cache = new AdvancedCache();


let users = [
  { 
    id: 1, 
    name: 'Sai', 
    email: 'sai@gmail.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  { 
    id: 2, 
    name: 'Teja', 
    email: 'teja@gmail.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];
let nextUserId = 3;


function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.endsWith('@gmail.com');
}


const CACHE_KEYS = {
  ALL_USERS: 'users:all',
  USER_BY_ID: (id) => `user:${id}`
};


function clearUserCache() {
  cache.delete(CACHE_KEYS.ALL_USERS);
  
  for (const key of cache.store.keys()) {
    if (key.startsWith('user:')) {
      cache.delete(key);
    }
  }
}


const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const method = req.method;
  const query = parsedUrl.query;
  
  
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Cache-Bypass');
  res.setHeader('Content-Type', 'application/json');
  
  
  if (method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  
  const sendResponse = (statusCode, data) => {
    res.writeHead(statusCode);
    res.end(JSON.stringify(data, null, 2));
  };
  

  if (path === '/health' && method === 'GET') {
    sendResponse(200, {
      success: true,
      status: 'OK',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cache: cache.getStats(),
      usersCount: users.length
    });
    return;
  }
  
  if (path === '/api/users' && method === 'GET') {
    
    const bypassCache = req.headers['x-cache-bypass'] === 'true';
    let cachedData = null;
    
    if (!bypassCache) {
      cachedData = cache.get(CACHE_KEYS.ALL_USERS);
    }
    
    if (cachedData && !bypassCache) {
      res.setHeader('X-Cache', 'HIT');
      res.setHeader('X-Cache-Key', CACHE_KEYS.ALL_USERS);
      sendResponse(200, {
        ...cachedData,
        _cached: true,
        _cacheHit: true,
        timestamp: new Date().toISOString()
      });
      return;
    }
    
    
    const search = query.search ? query.search.toLowerCase() : '';
    const page = parseInt(query.page) || 1;
    const limit = parseInt(query.limit) || 10;
    const sortBy = query.sortBy || 'id';
    const order = query.order === 'desc' ? 'desc' : 'asc';
    
    
    let filteredUsers = [...users];
    
    if (search) {
      filteredUsers = filteredUsers.filter(user =>
        user.name.toLowerCase().includes(search) ||
        user.email.toLowerCase().includes(search)
      );
    }
    
    
    filteredUsers.sort((a, b) => {
      if (order === 'asc') {
        return a[sortBy] > b[sortBy] ? 1 : -1;
      } else {
        return a[sortBy] < b[sortBy] ? 1 : -1;
      }
    });
    
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
    
    const response = {
      success: true,
      data: paginatedUsers,
      pagination: {
        total: filteredUsers.length,
        page,
        limit,
        totalPages: Math.ceil(filteredUsers.length / limit),
        hasNext: endIndex < filteredUsers.length,
        hasPrev: startIndex > 0
      },
      _cached: false,
      _cacheHit: false,
      timestamp: new Date().toISOString()
    };
    
    
    cache.set(CACHE_KEYS.ALL_USERS, response, 30000);
    
    res.setHeader('X-Cache', 'MISS');
    res.setHeader('X-Cache-Key', CACHE_KEYS.ALL_USERS);
    sendResponse(200, response);
    return;
  }
  
  
  if (path.startsWith('/api/users/') && method === 'GET') {
    const id = parseInt(path.split('/')[3]);
    
    if (isNaN(id)) {
      sendResponse(400, {
        success: false,
        error: 'Invalid user ID'
      });
      return;
    }
    
    const cacheKey = CACHE_KEYS.USER_BY_ID(id);
    const bypassCache = req.headers['x-cache-bypass'] === 'true';
    let cachedData = null;
    
    if (!bypassCache) {
      cachedData = cache.get(cacheKey);
    }
    
    if (cachedData && !bypassCache) {
      res.setHeader('X-Cache', 'HIT');
      res.setHeader('X-Cache-Key', cacheKey);
      sendResponse(200, {
        ...cachedData,
        _cached: true,
        _cacheHit: true
      });
      return;
    }
    
    const user = users.find(u => u.id === id);
    
    if (!user) {
      sendResponse(404, {
        success: false,
        error: `User with ID ${id} not found`
      });
      return;
    }
    
    const response = {
      success: true,
      data: user,
      _cached: false,
      _cacheHit: false
    };
    
    
    cache.set(cacheKey, response, 60000);
    
    res.setHeader('X-Cache', 'MISS');
    res.setHeader('X-Cache-Key', cacheKey);
    sendResponse(200, response);
    return;
  }
  
  
  if (path === '/api/users' && method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const { name, email } = data;
        

        if (!name || !email) {
          sendResponse(400, {
            success: false,
            error: 'Name and email are required'
          });
          return;
        }
        
        if (!isValidEmail(email)) {
          sendResponse(400, {
            success: false,
            error: 'Email must be a valid @gmail.com address'
          });
          return;
        }
        
        
        const emailExists = users.some(user => user.email === email);
        if (emailExists) {
          sendResponse(409, {
            success: false,
            error: `Email ${email} already exists`
          });
          return;
        }
        
        const now = new Date().toISOString();
        const newUser = {
          id: nextUserId++,
          name: name.trim(),
          email: email.toLowerCase(),
          createdAt: now,
          updatedAt: now
        };
        
        users.push(newUser);
        
        
        clearUserCache();
        
        console.log(`✅ User created: ${newUser.name} (${newUser.email})`);
        
        sendResponse(201, {
          success: true,
          message: 'User created successfully',
          data: newUser,
          cacheCleared: true
        });
      } catch (error) {
        sendResponse(400, {
          success: false,
          error: 'Invalid JSON format'
        });
      }
    });
    return;
  }
  
  
  if (path.startsWith('/api/users/') && method === 'PUT') {
    const id = parseInt(path.split('/')[3]);
    
    if (isNaN(id)) {
      sendResponse(400, {
        success: false,
        error: 'Invalid user ID'
      });
      return;
    }
    
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const { name, email } = data;
        
        const userIndex = users.findIndex(u => u.id === id);
        
        if (userIndex === -1) {
          sendResponse(404, {
            success: false,
            error: `User with ID ${id} not found`
          });
          return;
        }
        
        const updates = {};
        
        if (name !== undefined) {
          updates.name = name.trim();
        }
        
        if (email !== undefined) {
          if (!isValidEmail(email)) {
            sendResponse(400, {
              success: false,
              error: 'Email must be a valid @gmail.com address'
            });
            return;
          }
          
          
          const emailExists = users.some((user, index) => 
            user.email === email.toLowerCase() && index !== userIndex
          );
          
          if (emailExists) {
            sendResponse(409, {
              success: false,
              error: `Email ${email} already exists`
            });
            return;
          }
          
          updates.email = email.toLowerCase();
        }
        
        if (Object.keys(updates).length === 0) {
          sendResponse(400, {
            success: false,
            error: 'No valid fields to update'
          });
          return;
        }
        
        users[userIndex] = {
          ...users[userIndex],
          ...updates,
          updatedAt: new Date().toISOString()
        };
        
        
        clearUserCache();
        
        console.log(`✏️ User updated: ID ${id} (${users[userIndex].name})`);
        
        sendResponse(200, {
          success: true,
          message: 'User updated successfully',
          data: users[userIndex],
          cacheCleared: true
        });
      } catch (error) {
        sendResponse(400, {
          success: false,
          error: 'Invalid JSON format'
        });
      }
    });
    return;
  }
  
  
  if (path.startsWith('/api/users/') && method === 'DELETE') {
    const id = parseInt(path.split('/')[3]);
    
    if (isNaN(id)) {
      sendResponse(400, {
        success: false,
        error: 'Invalid user ID'
      });
      return;
    }
    
    const userIndex = users.findIndex(u => u.id === id);
    
    if (userIndex === -1) {
      sendResponse(404, {
        success: false,
        error: `User with ID ${id} not found`
      });
      return;
    }
    
    const deletedUser = users[userIndex];
    users.splice(userIndex, 1);
    
    
    clearUserCache();
    
    console.log(`🗑️ User deleted: ${deletedUser.name} (${deletedUser.email})`);
    
    sendResponse(200, {
      success: true,
      message: 'User deleted successfully',
      data: deletedUser,
      cacheCleared: true
    });
    return;
  }

  if (path === '/api/performance' && method === 'GET') {
    const startTime = process.hrtime();
    
    
    let results = [];
    for (let i = 0; i < 50000; i++) {
      results.push({
        id: i,
        value: Math.sqrt(i) * Math.random(),
        processed: new Date().toISOString()
      });
    }
    
    const endTime = process.hrtime(startTime);
    const processingTimeMs = (endTime[0] * 1000 + endTime[1] / 1000000).toFixed(2);
    
    sendResponse(200, {
      success: true,
      message: 'Performance test completed',
      results: {
        itemsProcessed: results.length,
        processingTime: `${processingTimeMs}ms`,
        operationsPerSecond: Math.round((results.length / processingTimeMs) * 1000),
        memoryUsage: process.memoryUsage()
      },
      timestamp: new Date().toISOString()
    });
    return;
  }
  
  
  if (path === '/api/cache/stats' && method === 'GET') {
    sendResponse(200, {
      success: true,
      data: cache.getStats(),
      timestamp: new Date().toISOString()
    });
    return;
  }
  

  if (path === '/api/cache/clear' && method === 'POST') {
    const oldStats = cache.getStats();
    cache.clear();
    
    sendResponse(200, {
      success: true,
      message: 'Cache cleared successfully',
      previousStats: oldStats,
      currentStats: cache.getStats(),
      timestamp: new Date().toISOString()
    });
    return;
  }
  
  
  if (path === '/' && method === 'GET') {
    sendResponse(200, {
      message: ' Optimized REST API with Caching',
      endpoints: [
        { method: 'GET', path: '/', description: 'List all endpoints' },
        { method: 'GET', path: '/health', description: 'Health check with stats' },
        { method: 'GET', path: '/api/users', description: 'Get all users (CACHED, supports search & pagination)' },
        { method: 'GET', path: '/api/users/:id', description: 'Get user by ID (CACHED)' },
        { method: 'POST', path: '/api/users', description: 'Create new user (@gmail.com required)' },
        { method: 'PUT', path: '/api/users/:id', description: 'Update user' },
        { method: 'DELETE', path: '/api/users/:id', description: 'Delete user' },
        { method: 'GET', path: '/api/performance', description: 'Performance test' },
        { method: 'GET', path: '/api/cache/stats', description: 'Cache statistics' },
        { method: 'POST', path: '/api/cache/clear', description: 'Clear all cache' }
      ],
      features: [
        ' Advanced caching with TTL',
        ' Email validation (@gmail.com required)',
        ' Proper cache invalidation',
        ' Search, sort, and pagination',
        ' Performance monitoring',
        ' CORS enabled',
        ' Error handling'
      ],
      timestamp: new Date().toISOString()
    });
    return;
  }
  
  
  sendResponse(404, {
    success: false,
    error: 'Route not found',
    path: path,
    method: method,
    timestamp: new Date().toISOString()
  });
});


const PORT = 3000;
server.listen(PORT, () => {
  console.log(`
==========================================================
 OPTIMIZED REST API WITH CACHING - STARTED SUCCESSFULLY
==========================================================
 Port: ${PORT}
 URL: http://localhost:${PORT}
 Time: ${new Date().toISOString()}
==========================================================


 QUICK TEST:
curl http://localhost:${PORT}/health
curl http://localhost:${PORT}/api/users
  `);
});

process.on('SIGINT', () => {
  console.log('\n Server shutting down gracefully...');
  console.log(' Final cache stats:', cache.getStats());
  console.log(' Total users:', users.length);
  process.exit(0);
});