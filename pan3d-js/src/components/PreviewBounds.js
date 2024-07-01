const { ref, toRefs, watch, onMounted } = window.Vue;

export default {
  props: {
    preview: {
      default: null,
    },
    axes: {
      default: null,
    },
    coordinates: {
      default: null,
    },
  },
  emits: ["update-bounds"],
  setup(props, { emit }) {
    const svg = ref();
    const { preview, coordinates } = toRefs(props);
    const previewImage = ref();
    const previewShape = ref();
    const viewBox = ref();
    const boundsBox = ref([0, 0, 0, 0]);
    let dragging = null;

    function updateViewBox() {
      const i = new Image();
      i.onload = () => {
        const factor = 300 / i.width;
        previewShape.value = [300, Math.round(i.height * factor)];
        viewBox.value = `0 0 ${previewShape.value.join(" ")}`;
      };
      i.src = preview.value;
    }

    function updateBoundsBox() {
      if (!previewShape.value) return;
      let xMin;
      let xMax;
      let yMin;
      let yMax;
      props.coordinates.forEach((coord) => {
        if (coord.name === props.axes.x) {
          let min =
            ((coord.bounds[0] - coord.full_bounds[0]) /
              (coord.full_bounds[1] - coord.full_bounds[0])) *
            previewShape.value[0];
          let max =
            ((coord.bounds[1] - coord.full_bounds[0]) /
              (coord.full_bounds[1] - coord.full_bounds[0])) *
            previewShape.value[0];
          if (coord.reverse_order === "True") {
            xMin = previewShape.value[0] - max;
            xMax = previewShape.value[0] - min;
          } else {
            xMin = min;
            xMax = max;
          }
        } else if (coord.name === props.axes.y) {
          let min =
            ((coord.bounds[0] - coord.full_bounds[0]) /
              (coord.full_bounds[1] - coord.full_bounds[0])) *
            previewShape.value[1];
          let max =
            ((coord.bounds[1] - coord.full_bounds[0]) /
              (coord.full_bounds[1] - coord.full_bounds[0])) *
            previewShape.value[1];
          // Y is reversed by default
          if (coord.reverse_order !== "True") {
            yMin = previewShape.value[1] - max;
            yMax = previewShape.value[1] - min;
          } else {
            yMin = min;
            yMax = max;
          }
        }
      });
      boundsBox.value = [xMin, yMin, xMax, yMax];
    }

    function onMousePress(e) {
      const allowance = 5;
      const svgBounds = svg.value.getBoundingClientRect();
      const location = [e.clientX - svgBounds.x, e.clientY - svgBounds.y];
      if (
        location[0] >= boundsBox.value[0] - allowance &&
        location[0] <= boundsBox.value[2] + allowance &&
        location[1] >= boundsBox.value[1] - allowance &&
        location[1] <= boundsBox.value[3] + allowance
      ) {
        dragging = {
          from: location,
          xMin: false,
          xMax: false,
          yMin: false,
          yMax: false,
          wholeBox: true,
        };
        if (Math.abs(location[0] - boundsBox.value[0]) <= allowance * 2) {
          dragging.xMin = true;
          dragging.wholeBox = false;
        }
        if (Math.abs(location[0] - boundsBox.value[2]) <= allowance * 2) {
          dragging.xMax = true;
          dragging.wholeBox = false;
        }
        if (Math.abs(location[1] - boundsBox.value[1]) <= allowance * 2) {
          dragging.yMin = true;
          dragging.wholeBox = false;
        }
        if (Math.abs(location[1] - boundsBox.value[3]) <= allowance * 2) {
          dragging.yMax = true;
          dragging.wholeBox = false;
        }
      }
    }

    function onMouseMove(e) {
      if (dragging) {
        const svgBounds = svg.value.getBoundingClientRect();
        const location = [e.clientX - svgBounds.x, e.clientY - svgBounds.y];
        const [dx, dy] = [
          location[0] - dragging.from[0],
          location[1] - dragging.from[1],
        ];
        dragging.from = location;
        let xMin = boundsBox.value[0];
        let yMin = boundsBox.value[1];
        let xMax = boundsBox.value[2];
        let yMax = boundsBox.value[3];
        if (dragging.xMin || dragging.xMax || dragging.wholeBox) {
          if (dragging.xMin || dragging.wholeBox) xMin += dx;
          if (dragging.xMax || dragging.wholeBox) xMax += dx;
          if (xMin >= 0 && xMax <= previewShape.value[0]) {
            boundsBox.value[0] = xMin;
            boundsBox.value[2] = xMax;
          }
        }
        if (dragging.yMin || dragging.yMax || dragging.wholeBox) {
          if (dragging.yMin || dragging.wholeBox) yMin += dy;
          if (dragging.yMax || dragging.wholeBox) yMax += dy;
          if (yMin >= 0 && yMax <= previewShape.value[1]) {
            boundsBox.value[1] = yMin;
            boundsBox.value[3] = yMax;
          }
        }
      }
    }

    function onMouseRelease() {
      if (dragging) {
        dragging = null;
        let xRange;
        let yRange;
        props.coordinates.forEach((coord) => {
          var coordRange = coord.full_bounds[1] - coord.full_bounds[0];
          if (coord.name === props.axes.x) {
            let xMin = boundsBox.value[0];
            let xMax = boundsBox.value[2];
            if (coord.reverse_order === "True") {
              xMin = previewShape.value[0] - boundsBox.value[2];
              xMax = previewShape.value[0] - boundsBox.value[0];
            }
            xRange = [
              (xMin / previewShape.value[0]) * coordRange + coord.full_bounds[0],
              (xMax / previewShape.value[0]) * coordRange + coord.full_bounds[0],
            ];
          } else if (coord.name === props.axes.y) {
            let yMin = boundsBox.value[1];
            let yMax = boundsBox.value[3];
            // Y is reversed by default
            if (coord.reverse_order !== "True") {
              yMin = previewShape.value[1] - boundsBox.value[3];
              yMax = previewShape.value[1] - boundsBox.value[1];
            }
            yRange = [
              (yMin / previewShape.value[1]) * coordRange + coord.full_bounds[0],
              (yMax / previewShape.value[1]) * coordRange + coord.full_bounds[0],
            ];
          }
        });
        emit("update-bounds", {
          name: props.axes.x,
          bounds: xRange.map((v) => Math.round(v)),
        });
        emit("update-bounds", {
          name: props.axes.y,
          bounds: yRange.map((v) => Math.round(v)),
        });
      }
    }

    onMounted(updateViewBox);
    watch(preview, updateViewBox);
    watch(previewShape, updateBoundsBox, { deep: true });
    watch(coordinates, updateBoundsBox, { deep: true });

    return {
      svg,
      preview,
      previewImage,
      viewBox,
      boundsBox,
      onMouseMove,
      onMousePress,
      onMouseRelease,
      color: "rgb(255, 0, 0)",
      outline: "4px solid rgb(0, 100, 255)",
      radius: 7,
    };
  },
  template: `
  <svg
    ref="svg"
    :viewBox="viewBox"
    @mousedown.prevent="onMousePress"
    @mousemove="onMouseMove"
    @mouseup="onMouseRelease"
    @mouseleave="onMouseRelease"
    :style="'cursor: pointer; outline:'+outline"
  >
    <image
      ref="previewImage"
      :href="preview"
      style="width: 300px"
    />
    <circle
      :cx="boundsBox[0]"
      :cy="boundsBox[1]"
      :r="radius"
      :fill="color"
    />
    <circle
      :cx="boundsBox[2]"
      :cy="boundsBox[1]"
      :r="radius"
      :fill="color"
    />
    <circle
      :cx="boundsBox[0]"
      :cy="boundsBox[3]"
      :r="radius"
      :fill="color"
    />
    <circle
      :cx="boundsBox[2]"
      :cy="boundsBox[3]"
      :r="radius"
      :fill="color"
    />
    <line
      :x1="boundsBox[0]"
      :y1="boundsBox[1]"
      :x2="boundsBox[2]"
      :y2="boundsBox[1]"
      :style="'stroke-width:5;stroke:'+color"
    />
    <line
      :x1="boundsBox[0]"
      :y1="boundsBox[1]"
      :x2="boundsBox[0]"
      :y2="boundsBox[3]"
      :style="'stroke-width:5;stroke:'+color"
    />
    <line
      :x1="boundsBox[2]"
      :y1="boundsBox[1]"
      :x2="boundsBox[2]"
      :y2="boundsBox[3]"
      :style="'stroke-width:5;stroke:'+color"
    />
    <line
      :x1="boundsBox[0]"
      :y1="boundsBox[3]"
      :x2="boundsBox[2]"
      :y2="boundsBox[3]"
      :style="'stroke-width:5;stroke:'+color"
    />
  </svg>
`,
};
