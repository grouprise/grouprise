const path = require("path");
const webpack = require("webpack");
const grunt = require("grunt");

const pkg = grunt.file.readJSON("package.json");
const raw_banner = grunt.file.read("res/templates/banner.txt");
const banner = grunt.template.process(raw_banner, { data: { package: pkg } });

module.exports = {
    entry: "./res/js/index.js",
    output: {
        filename: "./stadt/static/js/app.js"
    },
    resolve: {
        alias:{
            app: path.resolve(__dirname, "res/js")
        },
        extensions: ["", ".js"]
    },
    module: {
        noParse: /node_modules\/json-schema\/lib\/validate\.js/,
        loaders: [
            {
                test: /\.json$/,
                loader: "json-loader"
            },
            {
                test: /\.jsx?$/,
                exclude: /(node_modules|bower_components)/,
                cacheDirectory: __dirname + "/build/babel",
                loader: "babel",
                query: {
                    presets: ["es2015"],
                    plugins: ["transform-runtime"]
                }
            }
        ]
    },
    plugins: [
        new webpack.BannerPlugin(banner)
    ],
    node: {
        fs: "empty",
        net: "empty",
        tls: "empty"
    }
};
