#!/usr/bin/env node
// -*- coding: utf-8 -*-
// Filename: web/app.js
"use strict";

// Native imports
const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');

// NPM imports
const express = require('express');
const favicon = require('serve-favicon');
const mustache = require('mustache');

// Local imports
const settings = require('./settings');

process.title = 'C2 Web UI';
const template_dir = path.join(__dirname, 'templates');
const app = express();

// Functions
function render_template(template_name, context) {
    /*Render a specific template with a given context.

    Arguments:
        template_name (string): Name of the file within the template directory to render.
        context (object): Context information for rendering within the template.
    */
    return new Promise((resolve, reject) => {
        var template_path = path.join(template_dir, template_name);
        if (fs.existsSync(template_path)) {
            var contents = fs.readFileSync(template_path, 'utf-8');
            resolve(mustache.render(contents, context));
        } else {
            reject(`Template ${template_path} not found.`);
        }
    });
}

function start_server(app) {
    /*Create and start the server for the Gothmog web UI.

    Arguments:
        app (express): The express app to use for the server.
    */
    var server = null;
    if(settings['https']) {
        server = https.createServer({
            key: fs.readFileSync(settings['ssl_key_path']),
            cert: fs.readFileSync(settings['ssl_cert_path']),
            ca: fs.readFileSync(settings['ssl_ca_path'])
        }, app);
    } else {
        server = app;
    }
    server.listen(settings['webPort'], (err) => {
        if (err) {
            return console.log(`Error listening on port ${settings['webPort']}.`);
        }
        console.log(`${new Date()}: Web Server is listening on port ${settings['webPort']}.`);
    }).on('error', (err) => {
        if (err['code'] == 'EADDRINUSE') {
            console.log(`Port ${err['port']} is already in use on this machine, so the Gothmog web UI cannot launch.\n`);  
            console.log(`In order to proceed, please either change the settings to a different port,`)
            console.log(`or close the existing application on port ${err['port']}.`);
        } else {
            throw err;
        }
    });
}

// Common files
app.use('/css', express.static(path.join(__dirname, 'res', 'css')));
app.use('/media', express.static(path.join(__dirname, 'res', 'media')));
app.use('/javascripts', express.static(path.join(__dirname, 'res', 'javascripts')));

// Favicon
app.use(favicon(path.join(__dirname, 'res', 'favicon', 'favicon.ico')));

// Routes
app.use('/', (req, res) => {
    var context = {
        'site_url': settings['site_url'],
    };
    
    render_template('index.html', context)
    .then((html) => {
        res.status(200).send(html);
    })
    .catch((err) => {
        console.log(err);
        res.status(500).send('Server error.')
    });
});

start_server(app);
