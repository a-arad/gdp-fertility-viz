// Jest setup file for frontend tests
global.jest = require('jest');

// Mock DOM globals for jsdom environment
global.document = document;
global.window = window;
global.Event = window.Event;
global.setInterval = global.setInterval;
global.clearInterval = global.clearInterval;

// Mock console to avoid noisy output during tests
global.console = {
    ...console,
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
};