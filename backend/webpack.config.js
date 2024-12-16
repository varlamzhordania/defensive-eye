const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const {CleanWebpackPlugin} = require("clean-webpack-plugin");

module.exports = {
    entry: {
        base: './static/js/base.js',
    },
    output: {
        path: path.resolve(__dirname, './static/dist'),
        filename: 'js/[name]-bundle.js',
        library: ["SiteJS", "[name]"],
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx|ts|tsx)$/,
                exclude: /node_modules/,
                loader: "babel-loader",
            },
            {
                test: /\.css$/i,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'postcss-loader',
                ],
            },
        ],
    },
    resolve: {
        extensions: ['.js', '.jsx', '.ts', '.tsx', '.css'],
    },
    plugins: [
        new webpack.HotModuleReplacementPlugin(),
        new MiniCssExtractPlugin({
            filename: 'css/[name]-bundle.css',
        }),
        new CleanWebpackPlugin(),
    ],
    devtool: 'source-map',
    devServer: {
        static: {
            directory: path.join(__dirname, 'static'),
        },
        port: 3000,
        hot: true,
        open: true,
        liveReload: true,
        historyApiFallback: true,
    },
};
