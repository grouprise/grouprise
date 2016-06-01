require("es6-promise").polyfill();

module.exports = function (grunt) {
    var pkg = grunt.file.readJSON("package.json");

    // static files
    var raw_banner = grunt.file.read("res/templates/banner.txt");
    var banner = grunt.template.process(raw_banner, { data: { package: pkg } });

    // postcss config
    var postcss_autoprefixer = require("autoprefixer")({browsers: ["last 5 versions", "ie 11"]});
    var postcss_banner = require("postcss-banner")({ banner: banner });
    var postcss_wring = require("csswring");

    // Project configuration.
    grunt.initConfig({
        fontdump: {
            google: {
                options: {
                    web_directory: "../fonts"
                },
                files: {
                    "build/fonts/google/fonts.css":
                    "http://fonts.googleapis.com/css?family=" +
                    "Roboto Slab:300,400,700|" +
                    "Roboto:300,400,400italic,500,700"
                }
            }
        },
        less: {
            options: {
                strictMath: true,
                strictUnits: true,
                sourceMap: true,
                outputSourceFiles: true,
                compress: false
            },
            app: {
                options: {
                    sourceMapFilename: "build/css/app_unprefixed.css.map",
                    sourceMapURL: "./app_unprefixed.css.map"
                },
                files: {
                    "build/css/app_unprefixed.css": "res/less/app.less"
                }
            }
        },
        postcss: {
            options: {
                map: {
                    inline: false,
                    annotation: true,
                    prev: "build/css/app.css.map"
                },
                processors: [
                    postcss_autoprefixer,
                    postcss_wring,
                    postcss_banner
                ]
            },
            dist: {
                src: "build/css/app_unprefixed.css",
                dest: "stadt/static/css/app.css"
            }
        },
        exec: {
            webpack_dev: "node_modules/.bin/webpack",
            webpack_dist: "node_modules/.bin/webpack --optimize-minimize --optimize-occurence-order --optimize-dedupe"
        },
        copy: {
            fonts: {
                files: [
                    { cwd: "build/fonts/google", src: "*.!(css)", dest: "stadt/static/fonts", expand: true },
                    { cwd: "node_modules/font-awesome/fonts", src: "*", dest: "stadt/static/fonts", expand: true },
                    { cwd: "res/fonts", src: "**", dest: "stadt/static/fonts", expand: true }
                ]
            },
            images: {
                files: [
                    { cwd: "res/img", src: "**", dest: "stadt/static/img", expand: true }
                ]
            }
        },
        watch: {
            less: {
                files: ["res/**/*.less"],
                tasks: ["css"]
            }
        }
    });
    
    // These plugins provide necessary tasks.
    grunt.loadNpmTasks("grunt-contrib-watch");
    grunt.loadNpmTasks("grunt-contrib-less");
    grunt.loadNpmTasks("grunt-contrib-copy");
    grunt.loadNpmTasks("grunt-fontdump");
    grunt.loadNpmTasks("grunt-postcss");
    grunt.loadNpmTasks("grunt-exec");

    // Default task.
    grunt.registerTask("css", ["less", "postcss"]);
    grunt.registerTask("js", ["exec:webpack_dist"]);
    grunt.registerTask("fonts", ["fontdump", "copy:fonts"]);
    grunt.registerTask("images", ["copy:images"]);
    grunt.registerTask("default", ["fonts", "images", "css", "js"]);
};
