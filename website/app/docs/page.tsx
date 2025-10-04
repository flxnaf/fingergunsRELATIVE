import { Download, Camera, Settings, Play, Cpu, Monitor, AlertCircle } from 'lucide-react';

export default function Docs() {
  return (
    <div className="bg-black">
      {/* Hero Section */}
      <section className="py-24 px-6 lg:px-8 bg-gradient-to-b from-black via-gray-950 to-black">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="h1-text text-white mb-6">
            Documentation
          </h1>
          <p className="body-text text-gray-300 max-w-3xl mx-auto">
            Everything you need to get started with FingerGuns, from installation to advanced gesture controls.
          </p>
        </div>
      </section>

      {/* Quick Start Guide */}
      <section className="py-24 px-6 lg:px-8 bg-gray-950">
        <div className="max-w-5xl mx-auto">
          <h2 className="h2-text text-white mb-12 text-center">Quick Start Guide</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Step 1 */}
            <div className="bg-black border border-gray-800 p-6">
              <div className="w-12 h-12 bg-gray-800 flex items-center justify-center mb-4">
                <Download className="text-white" size={24} />
              </div>
              <div className="text-gray-500 body-text text-sm mb-2">Step 1</div>
              <h3 className="h4-text text-white mb-3">Download</h3>
              <p className="body-text text-sm text-gray-400">
                Download the latest version of FingerGuns and extract the files to your preferred location.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-black border border-gray-800 p-6">
              <div className="w-12 h-12 bg-gray-800 flex items-center justify-center mb-4">
                <Camera className="text-white" size={24} />
              </div>
              <div className="text-gray-500 body-text text-sm mb-2">Step 2</div>
              <h3 className="h4-text text-white mb-3">Camera Setup</h3>
              <p className="body-text text-sm text-gray-400">
                Position your webcam to capture both your face and hand gestures with good lighting.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-black border border-gray-800 p-6">
              <div className="w-12 h-12 bg-gray-800 flex items-center justify-center mb-4">
                <Settings className="text-white" size={24} />
              </div>
              <div className="text-gray-500 body-text text-sm mb-2">Step 3</div>
              <h3 className="h4-text text-white mb-3">Calibration</h3>
              <p className="body-text text-sm text-gray-400">
                Run the calibration utility to set your neutral positions and sensitivity preferences.
              </p>
            </div>

            {/* Step 4 */}
            <div className="bg-black border border-gray-800 p-6">
              <div className="w-12 h-12 bg-gray-800 flex items-center justify-center mb-4">
                <Play className="text-white" size={24} />
              </div>
              <div className="text-gray-500 body-text text-sm mb-2">Step 4</div>
              <h3 className="h4-text text-white mb-3">Start Gaming</h3>
              <p className="body-text text-sm text-gray-400">
                Launch CSGO, start FingerGuns, and experience gesture-based controls in action.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* System Requirements */}
      <section className="py-24 px-6 lg:px-8 bg-black">
        <div className="max-w-5xl mx-auto">
          <h2 className="h2-text text-white mb-12 text-center">System Requirements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Minimum Requirements */}
            <div className="bg-gray-950 border border-gray-800 p-8">
              <div className="flex items-center mb-6">
                <div className="w-10 h-10 bg-gray-800 flex items-center justify-center mr-4">
                  <Cpu className="text-white" size={20} />
                </div>
                <h3 className="h3-text text-white">Minimum</h3>
              </div>
              <ul className="space-y-3">
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">OS:</span> Windows 10 or later
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Processor:</span> Intel Core i5-4460 or equivalent
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Memory:</span> 8 GB RAM
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Camera:</span> 720p webcam at 30 FPS
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Python:</span> Python 3.8 or later
                </li>
              </ul>
            </div>

            {/* Recommended Requirements */}
            <div className="bg-gray-950 border border-gray-800 p-8">
              <div className="flex items-center mb-6">
                <div className="w-10 h-10 bg-gray-800 flex items-center justify-center mr-4">
                  <Monitor className="text-white" size={20} />
                </div>
                <h3 className="h3-text text-white">Recommended</h3>
              </div>
              <ul className="space-y-3">
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">OS:</span> Windows 11
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Processor:</span> Intel Core i7-8700K or equivalent
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Memory:</span> 16 GB RAM
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Camera:</span> 1080p webcam at 60 FPS
                </li>
                <li className="body-text text-sm text-gray-300">
                  <span className="text-white font-semibold">Python:</span> Python 3.10 or later
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Gesture Controls Reference */}
      <section className="py-24 px-6 lg:px-8 bg-gray-950">
        <div className="max-w-5xl mx-auto">
          <h2 className="h2-text text-white mb-12 text-center">Gesture Controls Reference</h2>
          
          {/* Hand Gestures */}
          <div className="mb-12">
            <h3 className="h3-text text-white mb-6">Hand Gestures</h3>
            <div className="bg-black border border-gray-800 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="body-text text-left text-white font-semibold p-4">Gesture</th>
                    <th className="body-text text-left text-white font-semibold p-4">Action</th>
                    <th className="body-text text-left text-white font-semibold p-4">Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Index Finger Point</td>
                    <td className="body-text text-sm text-gray-300 p-4">Aim Crosshair</td>
                    <td className="body-text text-sm text-gray-400 p-4">Move your index finger to aim</td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Hand Recoil</td>
                    <td className="body-text text-sm text-gray-300 p-4">Fire Weapon</td>
                    <td className="body-text text-sm text-gray-400 p-4">Quick backward hand motion triggers shooting</td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Thumb Up</td>
                    <td className="body-text text-sm text-gray-300 p-4">Switch Weapon Up</td>
                    <td className="body-text text-sm text-gray-400 p-4">Cycle to next weapon</td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Thumb Down</td>
                    <td className="body-text text-sm text-gray-300 p-4">Switch Weapon Down</td>
                    <td className="body-text text-sm text-gray-400 p-4">Cycle to previous weapon</td>
                  </tr>
                  <tr>
                    <td className="body-text text-sm text-gray-300 p-4">Closed Fist</td>
                    <td className="body-text text-sm text-gray-300 p-4">Reload</td>
                    <td className="body-text text-sm text-gray-400 p-4">Reload current weapon</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Head Movements */}
          <div>
            <h3 className="h3-text text-white mb-6">Head Movements</h3>
            <div className="bg-black border border-gray-800 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="body-text text-left text-white font-semibold p-4">Movement</th>
                    <th className="body-text text-left text-white font-semibold p-4">Action</th>
                    <th className="body-text text-left text-white font-semibold p-4">Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Tilt Forward</td>
                    <td className="body-text text-sm text-gray-300 p-4">Move Forward (W)</td>
                    <td className="body-text text-sm text-gray-400 p-4">Tilt head down to move forward</td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Tilt Backward</td>
                    <td className="body-text text-sm text-gray-300 p-4">Move Backward (S)</td>
                    <td className="body-text text-sm text-gray-400 p-4">Tilt head up to move backward</td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Tilt Left</td>
                    <td className="body-text text-sm text-gray-300 p-4">Strafe Left (A)</td>
                    <td className="body-text text-sm text-gray-400 p-4">Tilt head left to strafe left</td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="body-text text-sm text-gray-300 p-4">Tilt Right</td>
                    <td className="body-text text-sm text-gray-300 p-4">Strafe Right (D)</td>
                    <td className="body-text text-sm text-gray-400 p-4">Tilt head right to strafe right</td>
                  </tr>
                  <tr>
                    <td className="body-text text-sm text-gray-300 p-4">Nod Down Quickly</td>
                    <td className="body-text text-sm text-gray-300 p-4">Crouch</td>
                    <td className="body-text text-sm text-gray-400 p-4">Quick downward nod to crouch</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Troubleshooting */}
      <section className="py-24 px-6 lg:px-8 bg-black">
        <div className="max-w-5xl mx-auto">
          <h2 className="h2-text text-white mb-12 text-center">Troubleshooting</h2>
          <div className="space-y-6">
            {/* Issue 1 */}
            <div className="bg-gray-950 border border-gray-800 p-6">
              <div className="flex items-start">
                <AlertCircle className="text-white mr-4 flex-shrink-0 mt-1" size={20} />
                <div>
                  <h4 className="h4-text text-white mb-2">Hand tracking is not working</h4>
                  <p className="body-text text-sm text-gray-400 mb-2">
                    Ensure your hand is clearly visible in the camera frame with adequate lighting. Avoid backgrounds with similar skin tones or complex patterns.
                  </p>
                  <p className="body-text text-sm text-gray-500">
                    Try adjusting camera position or increasing ambient lighting.
                  </p>
                </div>
              </div>
            </div>

            {/* Issue 2 */}
            <div className="bg-gray-950 border border-gray-800 p-6">
              <div className="flex items-start">
                <AlertCircle className="text-white mr-4 flex-shrink-0 mt-1" size={20} />
                <div>
                  <h4 className="h4-text text-white mb-2">Controls are too sensitive or not sensitive enough</h4>
                  <p className="body-text text-sm text-gray-400 mb-2">
                    Run the calibration utility to adjust sensitivity thresholds and deadzones to match your movements.
                  </p>
                  <p className="body-text text-sm text-gray-500">
                    Settings can be fine-tuned in the configuration file.
                  </p>
                </div>
              </div>
            </div>

            {/* Issue 3 */}
            <div className="bg-gray-950 border border-gray-800 p-6">
              <div className="flex items-start">
                <AlertCircle className="text-white mr-4 flex-shrink-0 mt-1" size={20} />
                <div>
                  <h4 className="h4-text text-white mb-2">High latency or lag</h4>
                  <p className="body-text text-sm text-gray-400 mb-2">
                    Close other resource-intensive applications. Ensure your webcam is set to recommended resolution and frame rate.
                  </p>
                  <p className="body-text text-sm text-gray-500">
                    Lower camera resolution may improve performance on older systems.
                  </p>
                </div>
              </div>
            </div>

            {/* Issue 4 */}
            <div className="bg-gray-950 border border-gray-800 p-6">
              <div className="flex items-start">
                <AlertCircle className="text-white mr-4 flex-shrink-0 mt-1" size={20} />
                <div>
                  <h4 className="h4-text text-white mb-2">Python dependencies error</h4>
                  <p className="body-text text-sm text-gray-400 mb-2">
                    Ensure all required packages are installed: MediaPipe, OpenCV, PyAutoGUI, and NumPy. Run the included installation script.
                  </p>
                  <p className="body-text text-sm text-gray-500">
                    Check that you're using Python 3.8 or later.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

